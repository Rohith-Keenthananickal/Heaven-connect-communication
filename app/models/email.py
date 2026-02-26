"""
Email request and response models
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, model_validator
from app.templates.template_types import EmailTemplateType


class EmailTemplateContext(BaseModel):
    """
    Common variables used across email templates.
    Additional keys are allowed to support template-specific data.
    All fields are optional and should be provided based on the template type being used.
    """

    # Subject and recipient info
    subject: Optional[str] = Field(
        None, 
        description="Custom subject override for template-based emails. If not provided, template default subject will be used."
    )
    user_name: Optional[str] = Field(
        None, 
        description="Recipient name (used in greetings like 'Hello {user_name}')"
    )
    
    # Verification and authentication fields
    verification_link: Optional[str] = Field(
        None, 
        description="Email verification or account activation link (used in WELCOME, ACCOUNT_ACTIVATED templates)"
    )
    reset_link: Optional[str] = Field(
        None, 
        description="Password reset link used in forgot password emails (alternative to OTP)"
    )
    otp_code: Optional[str] = Field(
        None, 
        description="One-time password or verification code (used in EMAIL_VERIFICATION, PASSWORD_RESET templates). Typically 4-6 digits."
    )
    expiry_minutes: Optional[int] = Field(
        None, 
        description="Minutes remaining before an OTP or link expires. Used to display expiration time in email."
    )
    
    # Booking-related fields
    guest_name: Optional[str] = Field(
        None, 
        description="Guest name for booking notifications"
    )
    property_name: Optional[str] = Field(
        None, 
        description="Property name for booking notifications"
    )
    check_in_date: Optional[str] = Field(
        None, 
        description="ISO date for check-in (format: YYYY-MM-DD)"
    )
    check_out_date: Optional[str] = Field(
        None, 
        description="ISO date for check-out (format: YYYY-MM-DD)"
    )
    booking_id: Optional[str] = Field(
        None, 
        description="Booking identifier or reference number"
    )
    
    # Additional context
    additional_context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Catch-all for template-specific variables. Use this for any custom fields not listed above."
    )

    class Config:
        extra = "allow"
        json_schema_extra = {
            "examples": [
                {
                    "summary": "Email verification with OTP",
                    "value": {
                        "subject": "Verify Your Email - Heaven Connect",
                        "user_name": "John Doe",
                        "otp_code": "123456",
                        "expiry_minutes": 15
                    }
                },
                {
                    "summary": "Password reset with OTP",
                    "value": {
                        "user_name": "Jane Smith",
                        "otp_code": "789012",
                        "expiry_minutes": 10
                    }
                },
                {
                    "summary": "Welcome email with verification link",
                    "value": {
                        "subject": "Welcome to Heaven Connect",
                        "user_name": "John Doe",
                        "verification_link": "https://heavenconnect.com/verify?token=abc123"
                    }
                }
            ]
        }


class EmailRequest(BaseModel):
    """Request model for sending emails"""
    
    to: List[EmailStr] = Field(..., description="List of recipient email addresses")
    
    # Template-based email (preferred)
    template_type: Optional[EmailTemplateType] = Field(
        None,
        description="Email template type to use. If provided, template_context is required."
    )
    template_context: Optional[EmailTemplateContext] = Field(
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
            "examples": [
                {
                    "summary": "Email verification with OTP",
                    "description": "Send an email verification using OTP code",
                    "value": {
                        "to": ["user@example.com"],
                        "template_type": "EMAIL_VERIFICATION",
                        "template_context": {
                            "subject": "Welcome to Heaven Connect",
                            "user_name": "John Doe",
                            "otp_code": "123456",
                            "expiry_minutes": 15
                        }
                    }
                },
                {
                    "summary": "Welcome email with verification link",
                    "description": "Send a welcome email with verification link",
                    "value": {
                        "to": ["user@example.com"],
                        "template_type": "WELCOME",
                        "template_context": {
                            "user_name": "John Doe",
                            "verification_link": "https://heavenconnect.com/verify?token=abc123",
                            "subject": "Welcome to Heaven Connect"
                        }
                    }
                },
                {
                    "summary": "Password reset with OTP",
                    "description": "Send password reset email with OTP",
                    "value": {
                        "to": ["user@example.com"],
                        "template_type": "PASSWORD_RESET",
                        "template_context": {
                            "user_name": "John Doe",
                            "otp_code": "654321",
                            "expiry_minutes": 10
                        }
                    }
                },
                {
                    "summary": "Direct email (no template)",
                    "description": "Send a direct email without using a template",
                    "value": {
                        "to": ["user@example.com"],
                        "subject": "Custom Email Subject",
                        "body": "<h1>Hello!</h1><p>This is a custom email body.</p>",
                        "is_html": True
                    }
                }
            ]
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
