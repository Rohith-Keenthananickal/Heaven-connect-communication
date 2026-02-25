"""
Push notification request and response models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator, ConfigDict


class PushNotificationRequest(BaseModel):
    """Request model for sending push notifications
    
    Note: You need to provide at least ONE targeting method:
    - player_ids/user_ids: Target specific devices by OneSignal player IDs
    - subscription_ids: Target specific subscriptions (OneSignal subscription IDs)
    - segments: Target users by segment name
    
    You can use multiple targeting methods, and OneSignal will send to the union of all targets.
    """
    
    player_ids: Optional[List[str]] = Field(None, description="List of OneSignal player IDs to target")
    user_ids: Optional[List[str]] = Field(None, description="List of application user IDs (UUIDs) - will query Player table to get OneSignal IDs")
    subscription_ids: Optional[List[str]] = Field(None, description="List of OneSignal subscription IDs to target")
    segments: Optional[List[str]] = Field(None, description="List of OneSignal segments to target")
    headings: Dict[str, str] = Field(..., description="Notification headings in different languages")
    contents: Dict[str, str] = Field(..., description="Notification contents in different languages")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data payload")
    url: Optional[str] = Field(None, description="URL to open when notification is clicked")
    send_after: Optional[str] = Field(None, description="Schedule notification for later (ISO 8601 format)")
    priority: int = Field(10, ge=0, le=10, description="Notification priority (0-10)")
    
    @model_validator(mode='after')
    def validate_targeting(self):
        """Validate that at least one targeting method is provided"""
        # Note: user_ids will be processed in the router to query Player table
        # Don't map user_ids to player_ids here - they are different things
        
        # Validate that at least one targeting method is provided
        if not self.player_ids and not self.user_ids and not self.subscription_ids and not self.segments:
            raise ValueError(
                "At least one targeting method must be provided: "
                "player_ids, user_ids (application user IDs), subscription_ids, or segments"
            )
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_ids": ["user-id-1", "user-id-2"],
                "subscription_ids": ["subscription-id-1"],
                "segments": ["Active Users"],
                "headings": {"en": "New Booking"},
                "contents": {"en": "You have a new booking request"},
                "data": {"booking_id": "123", "type": "booking"},
                "url": "https://heavenconnect.com/bookings/123",
                "priority": 10
            }
        }
    )


class PushNotificationResponse(BaseModel):
    """Response model for push notification operations"""
    
    success: bool = Field(..., description="Whether the notification was sent successfully")
    notification_id: Optional[str] = Field(None, description="OneSignal notification ID if successful")
    recipients_count: Optional[int] = Field(None, description="Number of recipients")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "notification_id": "notification-id-123",
                "recipients_count": 2,
                "message": "Push notification sent successfully"
            }
        }
    )

