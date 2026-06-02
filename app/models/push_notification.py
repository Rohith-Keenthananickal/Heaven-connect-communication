"""
Push notification request and response models
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from app.models.openapi_notification_examples import SEND_PUSH_OPENAPI_EXAMPLES
from app.templates.push_template_types import PushNotificationTemplateType


class PushTemplateContext(BaseModel):
    """Variables substituted into push templates (Jinja2)."""

    host_name: Optional[str] = Field(None, description="Host display name")
    atp_name: Optional[str] = Field(None, description="ATP display name")
    guest_name: Optional[str] = Field(None, description="Guest display name")
    property_name: Optional[str] = Field(None, description="Property name")
    location: Optional[str] = Field(None, description="Location / area label")
    area: Optional[str] = Field(None, description="ATP assigned area")
    checkin_date: Optional[str] = Field(None, description="Check-in date")
    checkout_date: Optional[str] = Field(None, description="Check-out date")
    check_in_date: Optional[str] = Field(None, description="Check-in date alias")
    check_out_date: Optional[str] = Field(None, description="Check-out date alias")
    amount: Optional[str] = Field(None, description="Payment or refund amount")
    date: Optional[str] = Field(None, description="Maintenance or event date")

    class Config:
        extra = "allow"


def _unwrap_openapi_example_format(data: Any) -> Any:
    if isinstance(data, dict) and "value" in data and "user_ids" not in data and "player_ids" not in data:
        val = data.get("value")
        if isinstance(val, dict):
            return val
    return data


class PushNotificationRequest(BaseModel):
    """Request model for sending push notifications via OneSignal."""

    @model_validator(mode="before")
    @classmethod
    def unwrap_if_openapi_example_format(cls, data: Any) -> Any:
        return _unwrap_openapi_example_format(data)

    player_ids: Optional[List[str]] = Field(
        None,
        description="OneSignal player IDs (combined with IDs resolved from user_ids)",
    )
    user_ids: Optional[List[str]] = Field(
        None,
        description="Application user UUIDs — active Player rows are resolved to OneSignal targets",
    )
    subscription_ids: Optional[List[str]] = Field(
        None, description="OneSignal subscription IDs"
    )
    segments: Optional[List[str]] = Field(None, description="OneSignal segment names")

    template_type: Optional[PushNotificationTemplateType] = Field(
        None,
        description=(
            "Triphavenco push template from the notification matrix. "
            "When set, headings/contents are generated automatically; provide template_context for placeholders."
        ),
    )
    template_context: Optional[PushTemplateContext] = Field(
        None,
        description="Variables for template_type (e.g. host_name, property_name, guest_name, amount)",
    )
    language: str = Field(
        "en",
        description="Language key used for generated headings/contents (default: en)",
    )

    headings: Optional[Dict[str, str]] = Field(
        None,
        description="Notification titles per locale — required when template_type is omitted",
    )
    contents: Optional[Dict[str, str]] = Field(
        None,
        description="Notification bodies per locale — required when template_type is omitted",
    )

    data: Optional[Dict[str, Any]] = Field(
        None, description="Additional data payload (deep link hints, event type, etc.)"
    )
    url: Optional[str] = Field(None, description="URL opened when the notification is tapped")
    send_after: Optional[str] = Field(
        None, description="Schedule delivery (ISO 8601)"
    )
    priority: int = Field(10, ge=0, le=10, description="Delivery priority (0–10)")

    @model_validator(mode="after")
    def validate_targeting_and_content(self):
        if not self.player_ids and not self.user_ids and not self.subscription_ids and not self.segments:
            raise ValueError(
                "At least one targeting method is required: "
                "player_ids, user_ids, subscription_ids, or segments"
            )

        if self.template_type:
            if not self.template_context:
                self.template_context = PushTemplateContext()
        else:
            if not self.headings or not self.contents:
                raise ValueError(
                    "headings and contents are required when template_type is not provided"
                )

        return self


class PushNotificationResponse(BaseModel):
    """Response model for push notification operations."""

    success: bool = Field(..., description="Whether the notification was sent successfully")
    notification_id: Optional[str] = Field(
        None, description="OneSignal notification ID if successful"
    )
    recipients_count: Optional[int] = Field(None, description="Number of recipients")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "notification_id": "notification-id-123",
                "recipients_count": 2,
                "message": "Push notification sent successfully",
            }
        }
    }
