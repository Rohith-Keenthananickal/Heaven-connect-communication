"""
Push Notification API router
Handles HTTP endpoints for push notification operations
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.push_notification import PushNotificationRequest, PushNotificationResponse
from app.services.push_notification_service import PushNotificationService
from app.database import get_db
from app.models.player import Player, DeviceStatus

router = APIRouter(prefix="/api/push", tags=["Push Notifications"])

# Initialize push notification service
push_service = PushNotificationService()


@router.post("/send", response_model=PushNotificationResponse, status_code=status.HTTP_200_OK)
async def send_push_notification(
    notification_request: PushNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    Send a push notification using OneSignal API
    
    - **player_ids**: List of OneSignal player IDs to target directly
    - **user_ids**: List of application user IDs (UUIDs) - will query Player table to get OneSignal IDs
    - **subscription_ids**: List of OneSignal subscription IDs to target
    - **segments**: List of OneSignal segments to target
    - **headings**: Notification headings in different languages
    - **contents**: Notification contents in different languages
    - **data**: Additional data payload
    - **url**: URL to open when notification is clicked
    - **send_after**: Schedule notification for later (ISO 8601 format)
    - **priority**: Notification priority (0-10, default: 10)
    
    Note: At least one targeting method must be provided.
    If user_ids is provided, the system will query the Player table to get the corresponding OneSignal IDs.
    """
    try:
        # If user_ids are provided, query Player table to get OneSignal IDs
        external_user_ids: List[str] = []
        one_signal_ids: List[str] = []
        
        if notification_request.user_ids:
            # Query Player table for players with matching user_ids
            players = db.query(Player).filter(
                Player.user_id.in_(notification_request.user_ids),
                Player.status == DeviceStatus.ACTIVE  # Only active players
            ).all()
            
            if not players:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No active players found for the provided user_ids: {notification_request.user_ids}"
                )
            
            # Collect push_tokens and one_signal_ids
            for player in players:
                if player.push_token:
                    print("push_token", player.push_token)
                    external_user_ids.append(player.push_token)
                if player.one_signal_id:
                    one_signal_ids.append(player.one_signal_id)
            
            if not external_user_ids and not one_signal_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No valid push tokens or OneSignal IDs found for the provided user_ids"
                )
        
        # Combine player_ids: direct ones + ones from user_ids query
        final_player_ids = list(notification_request.player_ids) if notification_request.player_ids else []
        if one_signal_ids:
            final_player_ids.extend(one_signal_ids)
        
        result = await push_service.send_notification(
            player_ids=final_player_ids if final_player_ids else None,
            external_user_ids=external_user_ids if external_user_ids else None,
            subscription_ids=notification_request.subscription_ids,
            segments=notification_request.segments,
            headings=notification_request.headings,
            contents=notification_request.contents,
            data=notification_request.data,
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def push_health_check():
    """
    Health check endpoint for push notification service
    """
    return {
        "status": "healthy",
        "service": "push_notification",
        "provider": "onesignal",
    }

