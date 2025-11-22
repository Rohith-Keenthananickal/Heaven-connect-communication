"""
Push notification request and response models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PushNotificationRequest(BaseModel):
    """Request model for sending push notifications"""
    
    player_ids: Optional[List[str]] = Field(None, description="List of OneSignal user IDs (player IDs)")
    segments: Optional[List[str]] = Field(None, description="List of OneSignal segments to target")
    headings: Dict[str, str] = Field(..., description="Notification headings in different languages")
    contents: Dict[str, str] = Field(..., description="Notification contents in different languages")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data payload")
    url: Optional[str] = Field(None, description="URL to open when notification is clicked")
    send_after: Optional[str] = Field(None, description="Schedule notification for later (ISO 8601 format)")
    priority: int = Field(10, ge=0, le=10, description="Notification priority (0-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_ids": ["player-id-1", "player-id-2"],
                "headings": {"en": "New Booking"},
                "contents": {"en": "You have a new booking request"},
                "data": {"booking_id": "123", "type": "booking"},
                "url": "https://heavenconnect.com/bookings/123"
            }
        }


class PushNotificationResponse(BaseModel):
    """Response model for push notification operations"""
    
    success: bool = Field(..., description="Whether the notification was sent successfully")
    notification_id: Optional[str] = Field(None, description="OneSignal notification ID if successful")
    recipients_count: Optional[int] = Field(None, description="Number of recipients")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "notification_id": "notification-id-123",
                "recipients_count": 2,
                "message": "Push notification sent successfully"
            }
        }

