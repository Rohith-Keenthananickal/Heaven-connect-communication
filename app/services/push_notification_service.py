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
        # Configuration values are already stripped in Settings class
        self.app_id = settings.ONESIGNAL_APP_ID
        self.rest_api_key = settings.ONESIGNAL_REST_API_KEY
        self.api_url = settings.ONESIGNAL_API_URL
    
    async def send_notification(
        self,
        player_ids: Optional[List[str]] = None,
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
            player_ids: List of OneSignal user IDs (player IDs) to target
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
            if not self.app_id or not self.rest_api_key:
                app_id_preview = self.app_id[:10] if self.app_id else "(empty)"
                logger.error(f"OneSignal configuration incomplete. app_id: '{app_id_preview}...' (length: {len(self.app_id)}), rest_api_key: {'set' if self.rest_api_key else 'not set'}")
                return {
                    "success": False,
                    "notification_id": None,
                    "recipients_count": 0,
                    "message": "OneSignal configuration is incomplete",
                    "error": (
                        "OneSignal configuration is incomplete. Please check your .env file and ensure "
                        "ONESIGNAL_APP_ID and ONESIGNAL_REST_API_KEY are set and not empty."
                    ),
                }
            
            # Validate app_id format (OneSignal app IDs are UUIDs)
            if len(self.app_id) < 30:  # OneSignal app IDs are typically 36 characters (UUID format)
                app_id_preview = self.app_id[:20] if len(self.app_id) >= 20 else self.app_id
                logger.error(f"OneSignal app_id appears to be malformed. Length: {len(self.app_id)}, Value: '{app_id_preview}'")
                return {
                    "success": False,
                    "notification_id": None,
                    "recipients_count": 0,
                    "message": "OneSignal app_id is malformed",
                    "error": (
                        f"OneSignal app_id appears to be malformed. Expected a UUID format. "
                        f"Please check your ONESIGNAL_APP_ID in the .env file."
                    ),
                }
            
            # Validate REST API key format (OneSignal REST API keys are typically 40+ characters)
            if len(self.rest_api_key) < 30:
                api_key_preview = self.rest_api_key[:10] if self.rest_api_key else "(empty)"
                logger.error(f"OneSignal REST API key appears to be malformed. Length: {len(self.rest_api_key)}, Value: '{api_key_preview}...'")
                return {
                    "success": False,
                    "notification_id": None,
                    "recipients_count": 0,
                    "message": "OneSignal REST API key is malformed",
                    "error": (
                        f"OneSignal REST API key appears to be malformed or too short. "
                        f"Please check your ONESIGNAL_REST_API_KEY in the .env file. "
                        f"Get it from OneSignal Dashboard → Settings → Keys & IDs → REST API Key."
                    ),
                }
            
            if not player_ids and not segments:
                return {
                    "success": False,
                    "notification_id": None,
                    "recipients_count": 0,
                    "message": "Either player_ids or segments must be provided",
                    "error": "Missing target audience",
                }
            
            # Prepare notification payload
            notification_payload = {
                "app_id": self.app_id,
                "headings": headings or {"en": "Notification"},
                "contents": contents or {"en": "You have a new notification"},
                "priority": priority,
            }
            
            logger.debug(f"Sending push notification with app_id: {self.app_id[:10]}...")
            
            # Set target audience
            if player_ids:
                notification_payload["include_player_ids"] = player_ids
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
            
            # OneSignal requires Authorization header with REST API key
            # Format: Authorization: Basic <REST_API_KEY>
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {self.rest_api_key}",
            }
            
            logger.debug(f"Making request to OneSignal API: {api_url}")
            logger.debug(f"Authorization header present: {bool(self.rest_api_key)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    json=notification_payload,
                    headers=headers,
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                # Log full response for debugging
                logger.debug(f"OneSignal API response: {response_data}")
                
                # OneSignal API response fields can vary, try multiple possible field names
                notification_id = (
                    response_data.get("id") or 
                    response_data.get("notification_id") or 
                    response_data.get("notificationId")
                )
                
                recipients_count = (
                    response_data.get("recipients") or 
                    response_data.get("recipients_count") or
                    response_data.get("recipientsCount") or
                    0
                )
                
                # Check for errors or warnings in the response
                errors = response_data.get("errors", [])
                warnings = response_data.get("warnings", [])
                
                # If recipients_count is 0, it might mean the player_ids don't exist
                if recipients_count == 0 and player_ids:
                    logger.warning(
                        f"Notification sent but recipients_count is 0. "
                        f"This might mean the player_ids don't exist in OneSignal. "
                        f"Player IDs sent: {player_ids}"
                    )
                
                # Build response message
                message = "Push notification sent successfully"
                if recipients_count == 0:
                    message += " (but no recipients were found - player_ids may not exist in OneSignal)"
                if warnings:
                    message += f". Warnings: {', '.join(warnings)}"
                
                logger.info(
                    f"Push notification sent successfully. "
                    f"Notification ID: {notification_id}, "
                    f"Recipients: {recipients_count}, "
                    f"Errors: {errors}, "
                    f"Warnings: {warnings}"
                )
                
                return {
                    "success": True,
                    "notification_id": str(notification_id) if notification_id else None,
                    "recipients_count": recipients_count,
                    "message": message,
                }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error sending push notification: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            
            # Provide more specific error messages for common HTTP errors
            if e.response.status_code == 403:
                detailed_error = (
                    "OneSignal API returned 403 Forbidden. This usually means:\n"
                    "1. Your ONESIGNAL_REST_API_KEY is incorrect or missing\n"
                    "2. The REST API Key doesn't have the required permissions\n"
                    "3. The API key format is invalid\n\n"
                    "Please verify your REST API Key in OneSignal Dashboard:\n"
                    "Settings → Keys & IDs → REST API Key\n\n"
                    f"Original error: {e.response.text}"
                )
                logger.error(f"OneSignal authentication failed. API key length: {len(self.rest_api_key) if self.rest_api_key else 0}")
                return {
                    "success": False,
                    "notification_id": None,
                    "recipients_count": 0,
                    "message": "OneSignal API authentication failed",
                    "error": detailed_error,
                }
            
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

