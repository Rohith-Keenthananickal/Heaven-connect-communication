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
    
    # Host-related fields
    atp_name: Optional[str] = Field(
        None,
        description="Name of the ATP (Approval Team Person) for host registration notifications"
    )
    host_name: Optional[str] = Field(
        None,
        description="Name of the host for host registration notifications"
    )
    location: Optional[str] = Field(
        None,
        description="Location of the registered property for host registration notifications"
    )

    # Issue reporting fields
    issue: Optional[str] = Field(
        None,
        description="Summary of the support issue"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the support issue"
    )
    issue_code: Optional[str] = Field(
        None,
        description="Unique code or identifier for the support issue"
    )
    attachments: Optional[List[str]] = Field(
        None,
        description="List of image URLs attached to the support issue"
    )

    # Additional context
    additional_context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Catch-all for template-specific variables. Use this for any custom fields not listed above."
    )

    class Config:
        extra = "allow"
        # Each entry must be a real template_context object (not OpenAPI summary/value wrappers)
        json_schema_extra = {
            "examples": [
                {
                    "subject": "Verify Your Email - Heaven Connect",
                    "user_name": "John Doe",
                    "otp_code": "123456",
                    "expiry_minutes": 15,
                },
                {
                    "user_name": "Jane Smith",
                    "otp_code": "789012",
                    "expiry_minutes": 10,
                },
                {
                    "subject": "Welcome to Heaven Connect",
                    "user_name": "John Doe",
                    "verification_link": "https://heavenconnect.com/verify?token=abc123",
                },
            ]
        }


def _unwrap_openapi_example_format(data: Any) -> Any:
    """
    Unwrap request body if sent in OpenAPI example format.
    Some clients send: {"summary": "...", "description": "...", "value": {...}}
    """
    if isinstance(data, dict) and "value" in data and "to" not in data:
        val = data.get("value")
        if isinstance(val, dict):
            return val
    return data


class EmailRequest(BaseModel):
    """Request model for sending emails"""

    @model_validator(mode="before")
    @classmethod
    def unwrap_if_openapi_example_format(cls, data: Any) -> Any:
        return _unwrap_openapi_example_format(data)

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
        # Full request bodies only — do not wrap in { "summary", "value" } (that is not valid input)
        json_schema_extra = {
            "examples": [
                {
                    "to": ["user@example.com"],
                    "template_type": "EMAIL_VERIFICATION",
                    "template_context": {
                        "subject": "Welcome to Heaven Connect",
                        "user_name": "John Doe",
                        "otp_code": "123456",
                        "expiry_minutes": 15,
                    },
                },
                {
                    "to": ["user@example.com"],
                    "template_type": "WELCOME",
                    "template_context": {
                        "user_name": "John Doe",
                        "verification_link": "https://heavenconnect.com/verify?token=abc123",
                        "subject": "Welcome to Heaven Connect",
                    },
                },
                {
                    "to": ["user@example.com"],
                    "template_type": "PASSWORD_RESET",
                    "template_context": {
                        "user_name": "John Doe",
                        "otp_code": "654321",
                        "expiry_minutes": 10,
                    },
                },
                {
                    "summary": "Support issue created",
                    "description": "Notify user about a newly created support issue",
                    "value": {
                        "to": ["user@example.com"],
                        "template_type": "SUPPORT_CREATED",
                        "template_context": {
                            "user_name": "John Doe",
                            "issue": "Login problem",
                            "description": "Cannot log in to my account after password reset.",
                            "property_name": "Heaven Connect Platform",
                            "issue_code": "HC-001-2026",
                            "attachments": [
                                "https://example.com/image1.png",
                                "https://example.com/image2.jpg"
                            ]
                        }
                    }
                },
                {
                    "summary": "New Host Registration ATP Notification",
                    "description": "Inform ATP about a new host registration",
                    "value": {
                        "to": ["atp_email@example.com"],
                        "template_type": "HOST_REGISTRATION_ATP",
                        "template_context": {
                            "atp_name": "ATP Team",
                            "host_name": "New Host",
                            "location": "Some City, Some Country"
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
                },
            ]
        }


class EmailResponse(BaseModel):
    """Response model for email sending operations"""
    
    success: bool = Field(..., description="Whether the email was sent successfully")
    message_id: Optional[str] = Field(None, description="Provider message ID if successful")
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
