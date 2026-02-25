"""
Push Notification API router
Handles HTTP endpoints for push notification operations
"""

from fastapi import APIRouter, HTTPException, status
from app.models.push_notification import PushNotificationRequest, PushNotificationResponse
from app.services.push_notification_service import PushNotificationService

router = APIRouter(prefix="/api/push", tags=["Push Notifications"])

# Initialize push notification service
push_service = PushNotificationService()


@router.post("/send", response_model=PushNotificationResponse, status_code=status.HTTP_200_OK)
async def send_push_notification(notification_request: PushNotificationRequest):
    """
    Send a push notification using OneSignal API
    
    - **player_ids/user_ids**: List of OneSignal player IDs to target
    - **subscription_ids**: List of OneSignal subscription IDs to target
    - **segments**: List of OneSignal segments to target
    - **headings**: Notification headings in different languages
    - **contents**: Notification contents in different languages
    - **data**: Additional data payload
    - **url**: URL to open when notification is clicked
    - **send_after**: Schedule notification for later (ISO 8601 format)
    - **priority**: Notification priority (0-10, default: 10)
    
    Note: At least one targeting method (player_ids, subscription_ids, or segments) must be provided.
    """
    try:
        result = await push_service.send_notification(
            player_ids=notification_request.player_ids,
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

