"""
Zoho Email Service
Handles email sending using Zoho Mail API with OAuth2 authentication
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import settings
from app.templates.template_loader import TemplateLoader
from app.templates.template_types import EmailTemplateType

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Zoho Mail API"""
    
    def __init__(self):
        self.client_id = settings.ZOHO_CLIENT_ID
        self.client_secret = settings.ZOHO_CLIENT_SECRET
        self.refresh_token = settings.ZOHO_REFRESH_TOKEN
        self.account_id = settings.ZOHO_ACCOUNT_ID
        self.from_email = settings.ZOHO_FROM_EMAIL
        self.from_name = settings.ZOHO_FROM_NAME
        self.api_domain = settings.ZOHO_API_DOMAIN
        self._access_token: Optional[str] = None
    
    async def _get_access_token(self) -> str:
        """
        Get or refresh Zoho OAuth2 access token
        Uses refresh token to obtain a new access token
        """
        # Validate configuration before attempting to get token
        if not settings.validate_zoho_config():
            raise ValueError(
                "Zoho configuration is incomplete. Please check your .env file and ensure "
                "ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN, "
                "ZOHO_ACCOUNT_ID, and ZOHO_FROM_EMAIL are set."
            )
        
        if self._access_token:
            return self._access_token
        
        token_endpoint = "https://accounts.zoho.in/oauth/v2/token"
        
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                }
                print("--------------------------------")
                print("Payload:", payload)
                print("--------------------------------")
                response = await client.post(
                    token_endpoint,
                    data=payload,
                )
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                
                if not self._access_token:
                    raise ValueError("Failed to obtain access token from Zoho")
                
                logger.info("Successfully obtained Zoho access token")
                return self._access_token
                
            except httpx.HTTPError as e:
                logger.error(f"Error obtaining Zoho access token: {e}")
                raise Exception(f"Failed to authenticate with Zoho: {str(e)}")
    
    async def send_email(
        self,
        to: List[str],
        subject: Optional[str] = None,
        body: Optional[str] = None,
        template_type: Optional[EmailTemplateType] = None,
        template_context: Optional[Dict[str, Any]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        is_html: bool = True,
        reply_to: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> dict:
        """
        Send an email using Zoho Mail API
        
        Args:
            to: List of recipient email addresses
            subject: Email subject (required if template_type not provided)
            body: Email body (required if template_type not provided)
            template_type: Email template type (optional)
            template_context: Context variables for template (required if template_type provided)
            cc: Optional list of CC email addresses
            bcc: Optional list of BCC email addresses
            is_html: Whether the body is HTML content
            reply_to: Optional reply-to email address
            attachments: Optional list of attachment file paths
            
        Returns:
            dict: Response containing message_id and status
        """
        try:
            # Configuration validation happens in _get_access_token
            access_token = await self._get_access_token()
            
            # Handle template-based email
            if template_type:
                if not template_context:
                    return {
                        "success": False,
                        "message_id": None,
                        "message": "template_context is required when template_type is provided",
                        "error": "Missing template_context",
                    }
                
                try:
                    # Add current year to context if not present
                    from datetime import datetime
                    if "current_year" not in template_context:
                        template_context["current_year"] = datetime.now().year
                    
                    rendered_subject, rendered_body = TemplateLoader.render_template(
                        template_type=template_type,
                        context=template_context
                    )
                    subject = subject or rendered_subject
                    body = rendered_body
                    is_html = True  # Templates are always HTML
                except Exception as e:
                    return {
                        "success": False,
                        "message_id": None,
                        "message": "Failed to render email template",
                        "error": str(e),
                    }
            else:
                # Direct email content
                if not subject or not body:
                    return {
                        "success": False,
                        "message_id": None,
                        "message": "subject and body are required when template_type is not provided",
                        "error": "Missing subject or body",
                    }
            
            # Prepare email payload according to Zoho Mail API format
            # Based on Zoho Mail API v1 documentation
            email_payload = {
                "fromAddress": self.from_email,
                "toAddress": ",".join(to),  # Comma-separated string
                "subject": subject,
                "content": body,
            }
            
            # Set content type
            if is_html:
                email_payload["mailFormat"] = "html"
            else:
                email_payload["mailFormat"] = "text"
            
            # Add optional fields (only if provided)
            if cc:
                email_payload["ccAddress"] = ",".join(cc)
            if bcc:
                email_payload["bccAddress"] = ",".join(bcc)
            if reply_to:
                email_payload["replyToAddress"] = reply_to
            
            # Zoho Mail API endpoint
            api_url = f"{self.api_domain}/api/accounts/{self.account_id}/messages"
            
            headers = {
                "Authorization": f"Zoho-oauthtoken {access_token}",
                "Content-Type": "application/json",
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    json=email_payload,
                    headers=headers,
                )
                
                response.raise_for_status()
                response_data = response.json()
                
                # Extract message ID from response
                message_id = response_data.get("data", {}).get("messageId") or response_data.get("messageId")
                
                logger.info(f"Email sent successfully. Message ID: {message_id}")
                
                return {
                    "success": True,
                    "message_id": str(message_id) if message_id else None,
                    "message": "Email sent successfully",
                }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error sending email: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "message_id": None,
                "message": "Failed to send email",
                "error": error_msg,
            }
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message_id": None,
                "message": "Failed to send email",
                "error": error_msg,
            }

