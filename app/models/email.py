"""
Email request and response models
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, model_validator
from app.templates.template_types import EmailTemplateType


class EmailRequest(BaseModel):
    """Request model for sending emails"""
    
    to: List[EmailStr] = Field(..., description="List of recipient email addresses")
    
    # Template-based email (preferred)
    template_type: Optional[EmailTemplateType] = Field(
        None,
        description="Email template type to use. If provided, template_context is required."
    )
    template_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Context variables for template rendering (required if template_type is provided)"
    )
    
    # Direct email content (alternative to template)
    subject: Optional[str] = Field(None, min_length=1, description="Email subject (required if template_type is not provided)")
    body: Optional[str] = Field(None, min_length=1, description="Email body (HTML or plain text, required if template_type is not provided)")
    
    cc: Optional[List[EmailStr]] = Field(None, description="List of CC email addresses")
    bcc: Optional[List[EmailStr]] = Field(None, description="List of BCC email addresses")
    is_html: bool = Field(True, description="Whether the body is HTML content")
    reply_to: Optional[EmailStr] = Field(None, description="Reply-to email address")
    attachments: Optional[List[str]] = Field(None, description="List of attachment file paths")
    
    @model_validator(mode='after')
    def validate_content(self):
        """Validate that either template or direct content is provided"""
        if self.template_type:
            if not self.template_context:
                raise ValueError("template_context is required when template_type is provided")
        else:
            if not self.subject or not self.body:
                raise ValueError("subject and body are required when template_type is not provided")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "to": ["user@example.com"],
                "template_type": "welcome",
                "template_context": {
                    "user_name": "John Doe",
                    "verification_link": "https://heavenconnect.com/verify?token=abc123"
                }
            }
        }


class EmailResponse(BaseModel):
    """Response model for email sending operations"""
    
    success: bool = Field(..., description="Whether the email was sent successfully")
    message_id: Optional[str] = Field(None, description="Zoho message ID if successful")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message_id": "123456789",
                "message": "Email sent successfully"
            }
        }


class ScheduledEmailRequest(BaseModel):
    """Request model for scheduling emails (combines email and schedule)"""
    
    email: EmailRequest = Field(..., description="Email request details")
    schedule: "ScheduleRequest" = Field(..., description="Schedule configuration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": {
                    "to": ["user@example.com"],
                    "template_type": "booking_reminder",
                    "template_context": {
                        "guest_name": "John Doe",
                        "property_name": "Beach Villa"
                    }
                },
                "schedule": {
                    "schedule_type": "monthly",
                    "monthly_day": 15,
                    "monthly_time": "09:00"
                }
            }
        }


# Import ScheduleRequest at the end to resolve forward reference
# This avoids circular import issues
from app.models.schedule import ScheduleRequest
ScheduledEmailRequest.model_rebuild()
