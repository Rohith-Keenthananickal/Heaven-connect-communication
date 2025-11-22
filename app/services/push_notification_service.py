"""
OneSignal Push Notification Service
Handles push notifications using OneSignal API
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications via OneSignal API"""
    
    def __init__(self):
        self.app_id = settings.ONESIGNAL_APP_ID
        self.rest_api_key = settings.ONESIGNAL_REST_API_KEY
        self.api_url = settings.ONESIGNAL_API_URL
    
    async def send_notification(
        self,
        user_ids: Optional[List[str]] = None,
        segments: Optional[List[str]] = None,
        headings: Dict[str, str] = None,
        contents: Dict[str, str] = None,
        data: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
        send_after: Optional[str] = None,
        priority: int = 10,
    ) -> dict:
        """
        Send a push notification using OneSignal API
        
        Args:
            user_ids: List of OneSignal user IDs (player IDs) to target
            segments: List of OneSignal segments to target
            headings: Notification headings in different languages
            contents: Notification contents in different languages
            data: Additional data payload
            url: URL to open when notification is clicked
            send_after: Schedule notification for later (ISO 8601 format)
            priority: Notification priority (0-10)
            
        Returns:
            dict: Response containing notification_id and status
        """
        try:
            # Validate configuration before attempting to send notification
            if not settings.validate_onesignal_config():
                return {
                    "success": False,
                    "notification_id": None,
                    "recipients_count": 0,
                    "message": "OneSignal configuration is incomplete",
                    "error": (
                        "OneSignal configuration is incomplete. Please check your .env file and ensure "
                        "ONESIGNAL_APP_ID and ONESIGNAL_REST_API_KEY are set."
                    ),
                }
            
            if not user_ids and not segments:
                return {
                    "success": False,
                    "notification_id": None,
                    "recipients_count": 0,
                    "message": "Either user_ids or segments must be provided",
                    "error": "Missing target audience",
                }
            
            # Prepare notification payload
            notification_payload = {
                "app_id": self.app_id,
                "headings": headings or {"en": "Notification"},
                "contents": contents or {"en": "You have a new notification"},
                "priority": priority,
            }
            
            # Set target audience
            if user_ids:
                notification_payload["include_player_ids"] = user_ids
            elif segments:
                notification_payload["included_segments"] = segments
            
            # Add optional fields
            if data:
                notification_payload["data"] = data
            
            if url:
                notification_payload["url"] = url
            
            if send_after:
                notification_payload["send_after"] = send_after
            
            # OneSignal API endpoint
            api_url = f"{self.api_url}/notifications"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {self.rest_api_key}",
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    json=notification_payload,
                    headers=headers,
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                notification_id = response_data.get("id")
                recipients_count = response_data.get("recipients", 0)
                
                logger.info(
                    f"Push notification sent successfully. "
                    f"Notification ID: {notification_id}, "
                    f"Recipients: {recipients_count}"
                )
                
                return {
                    "success": True,
                    "notification_id": str(notification_id) if notification_id else None,
                    "recipients_count": recipients_count,
                    "message": "Push notification sent successfully",
                }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error sending push notification: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "notification_id": None,
                "recipients_count": 0,
                "message": "Failed to send push notification",
                "error": error_msg,
            }
        except Exception as e:
            error_msg = f"Error sending push notification: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "notification_id": None,
                "recipients_count": 0,
                "message": "Failed to send push notification",
                "error": error_msg,
            }

