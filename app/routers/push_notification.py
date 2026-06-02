"""
Push Notification API router
Handles HTTP endpoints for push notification operations
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.player import DeviceStatus, Player
from app.models.push_notification import (
    SEND_PUSH_OPENAPI_EXAMPLES,
    PushNotificationRequest,
    PushNotificationResponse,
)
from app.services.push_notification_service import PushNotificationService
from app.templates.push_template_loader import PushTemplateLoader
from app.templates.push_template_types import PushNotificationTemplateType

router = APIRouter(prefix="/api/push", tags=["Push Notifications"])

push_service = PushNotificationService()


def _resolve_headings_and_contents(
    notification_request: PushNotificationRequest,
) -> tuple[Dict[str, str], Dict[str, str]]:
    if not notification_request.template_type:
        return notification_request.headings, notification_request.contents

    context: Dict[str, Any] = {}
    if notification_request.template_context:
        context = notification_request.template_context.model_dump(exclude_none=True)

    try:
        return PushTemplateLoader.render_template(
            template_type=notification_request.template_type,
            context=context,
            language=notification_request.language,
        )
    except Exception as e:
        raise ValueError(f"Failed to render push template: {e}") from e


def _merge_data_payload(
    notification_request: PushNotificationRequest,
) -> Dict[str, Any] | None:
    data = dict(notification_request.data) if notification_request.data else {}
    if notification_request.template_type:
        data.setdefault("template_type", notification_request.template_type.value)
    return data or None


@router.get("/templates", status_code=status.HTTP_200_OK)
async def list_push_templates():
    """
    List all predefined push notification templates (title + message patterns).

    Patterns use Jinja2 placeholders (e.g. `{{ host_name }}`, `{{ property_name }}`).
    Events marked N/A for push in the matrix (OTP, ATP/Host registration submitted) are omitted.
    """
    return {"templates": PushTemplateLoader.list_templates()}


@router.post("/send", response_model=PushNotificationResponse, status_code=status.HTTP_200_OK)
async def send_push_notification(
    notification_request: PushNotificationRequest = Body(
        ...,
        openapi_examples=SEND_PUSH_OPENAPI_EXAMPLES,
        description="Send a Triphavenco templated or custom push via OneSignal.",
    ),
    db: Session = Depends(get_db),
):
    """
    Send a push notification using the OneSignal API.

    ## Modes

    1. **Template-based** — set `template_type` + optional `template_context` (recommended).
       Title and body come from the [notification matrix](https://docs.google.com/spreadsheets/d/1Ma2X4mNl68PNJdeFJrtfkrqNqErNVBUJYiIEEBQekY0).
    2. **Custom** — set `headings` and `contents` directly (per locale).

    Use the **Examples** dropdown in Swagger to pre-fill common requests.

    ## Targeting (at least one required)

    | Field | Description |
    |-------|-------------|
    | `user_ids` | App user UUIDs — resolves active `Player` rows to OneSignal player / external IDs |
    | `player_ids` | OneSignal player IDs (also merged with IDs from `user_ids`) |
    | `subscription_ids` | OneSignal subscription IDs |
    | `segments` | OneSignal audience segments |

    ## Template types

    | Category | template_type | Context fields |
    |----------|---------------|----------------|
    | ATP | HOST_REGISTRATION_ATP | host_name, location |
    | ATP | NEW_PROPERTY_SUBMITTED_ATP, PROPERTY_UPDATED_ATP | property_name, host_name |
    | ATP | NEW_BOOKING_ATP | property_name, guest_name |
    | ATP | GUEST_COMPLAINT_ATP | property_name |
    | ATP | HOST_SUSPENDED_ATP | host_name |
    | ATP | ATP_APPROVED, ATP_REJECTED, ATP_ACCOUNT_* | (optional) |
    | ATP | ATP_ASSIGNED_AREA | area |
    | Host | HOST_ACCOUNT_APPROVED, HOST_ACCOUNT_REJECTED, HOST_ACCOUNT_SUSPENDED | — |
    | Host | PROPERTY_APPROVED, PROPERTY_REJECTED | property_name |
    | Host | NEW_BOOKING_RECEIVED_HOST, HOST_BOOKING_CANCELLED | property_name |
    | Host | GUEST_CHECK_IN_REMINDER_HOST | guest_name, checkin_date |
    | Host | REVIEW_RECEIVED | guest_name |
    | Common | PAYMENT_RECEIVED, PAYMENT_FAILED, REFUND_ISSUED | amount |
    | Common | PASSWORD_RESET, PASSWORD_RESET_SUCCESSFUL, NEW_OFFER | — |
    | Common | MAINTENANCE_ALERT | date |
    | Common | APP_UPDATE_AVAILABLE | — |

    See `GET /api/push/templates` for the full static title/message list.

    ## Other fields

    - **language** — locale key for generated copy (default `en`)
    - **data** — custom payload; `template_type` is added automatically when using a template
    - **url** — deep link opened on tap
    - **send_after** — ISO 8601 scheduled delivery
    - **priority** — 0–10 (default 10)
    """
    try:
        headings, contents = _resolve_headings_and_contents(notification_request)
        data = _merge_data_payload(notification_request)

        external_user_ids: List[str] = []
        one_signal_ids: List[str] = []

        if notification_request.user_ids:
            players = (
                db.query(Player)
                .filter(
                    Player.user_id.in_(notification_request.user_ids),
                    Player.status == DeviceStatus.ACTIVE,
                )
                .all()
            )

            if not players:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        "No active players found for user_ids: "
                        f"{notification_request.user_ids}"
                    ),
                )

            for player in players:
                if player.push_token:
                    external_user_ids.append(player.push_token)
                if player.one_signal_id:
                    one_signal_ids.append(player.one_signal_id)

            if not external_user_ids and not one_signal_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No valid push tokens or OneSignal IDs found for the provided user_ids",
                )

        final_player_ids = (
            list(notification_request.player_ids) if notification_request.player_ids else []
        )
        if one_signal_ids:
            final_player_ids.extend(one_signal_ids)

        result = await push_service.send_notification(
            player_ids=final_player_ids if final_player_ids else None,
            external_user_ids=external_user_ids if external_user_ids else None,
            subscription_ids=notification_request.subscription_ids,
            segments=notification_request.segments,
            headings=headings,
            contents=contents,
            data=data,
            url=notification_request.url,
            send_after=notification_request.send_after,
            priority=notification_request.priority,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send push notification"),
            )

        return PushNotificationResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def push_health_check():
    """Health check for the push notification service."""
    return {
        "status": "healthy",
        "service": "push_notification",
        "provider": "onesignal",
    }
