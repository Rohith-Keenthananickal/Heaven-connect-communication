"""
Email request and response models
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.templates.template_types import EmailTemplateType


SEND_EMAIL_OPENAPI_EXAMPLES: Dict[str, Dict[str, Any]] = {
    "email_verification": {
        "summary": "Email verification with OTP",
        "description": "Send an email verification using OTP code",
        "value": {
            "to": ["user@example.com"],
            "template_type": "EMAIL_VERIFICATION",
            "template_context": {
                "subject": "Welcome to Heaven Connect",
                "user_name": "John Doe",
                "otp_code": "123456",
                "expiry_minutes": 15,
            },
        },
    },
    "support_created": {
        "summary": "Support issue created",
        "description": "Notify user after creating a support issue",
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
                    "https://example.com/image2.jpg",
                ],
            },
        },
    },
    "host_registration_atp": {
        "summary": "New Host Registration ATP Notification",
        "description": "Inform ATP about a new host registration",
        "value": {
            "to": ["atp_email@example.com"],
            "template_type": "HOST_REGISTRATION_ATP",
            "template_context": {
                "atp_name": "ATP Team",
                "host_name": "New Host",
                "location": "Some City, Some Country",
            },
        },
    },
    "direct_email": {
        "summary": "Direct email (no template)",
        "description": "Send a direct email without using a template",
        "value": {
            "to": ["user@example.com"],
            "subject": "Custom Email Subject",
            "body": "<h1>Hello!</h1><p>This is a custom email body.</p>",
            "is_html": True,
        },
    },
}


class EmailTemplateContext(BaseModel):
    """Common variables used across email templates."""

    subject: Optional[str] = Field(None, description="Custom subject override for template emails")
    user_name: Optional[str] = Field(None, description="Recipient name")

    verification_link: Optional[str] = Field(None, description="Email verification link")
    reset_link: Optional[str] = Field(None, description="Password reset link")
    otp_code: Optional[str] = Field(None, description="One-time password")
    expiry_minutes: Optional[int] = Field(None, description="Expiry time in minutes")

    guest_name: Optional[str] = Field(None, description="Guest name")
    property_name: Optional[str] = Field(None, description="Property name")
    check_in_date: Optional[str] = Field(None, description="Check-in date")
    check_out_date: Optional[str] = Field(None, description="Check-out date")
    booking_id: Optional[str] = Field(None, description="Booking identifier")

    atp_name: Optional[str] = Field(None, description="ATP name")
    host_name: Optional[str] = Field(None, description="Host name")
    location: Optional[str] = Field(None, description="Property location")

    issue: Optional[str] = Field(None, description="Support issue summary")
    description: Optional[str] = Field(None, description="Support issue description")
    issue_code: Optional[str] = Field(None, description="Support issue code")
    attachments: Optional[List[str]] = Field(None, description="Attachment image URLs")

    additional_context: Optional[Dict[str, Any]] = Field(None, description="Extra template fields")

    class Config:
        extra = "allow"


def _unwrap_openapi_example_format(data: Any) -> Any:
    if isinstance(data, dict) and "value" in data and "to" not in data:
        val = data.get("value")
        if isinstance(val, dict):
            return val
    return data


class EmailRequest(BaseModel):
    """Request model for sending emails."""

    @model_validator(mode="before")
    @classmethod
    def unwrap_if_openapi_example_format(cls, data: Any) -> Any:
        return _unwrap_openapi_example_format(data)

    to: List[EmailStr] = Field(..., description="List of recipient email addresses")
    template_type: Optional[EmailTemplateType] = Field(None, description="Email template type")
    template_context: Optional[EmailTemplateContext] = Field(None, description="Template variables")

    subject: Optional[str] = Field(None, min_length=1, description="Email subject")
    body: Optional[str] = Field(None, min_length=1, description="Email body")

    cc: Optional[List[EmailStr]] = Field(None, description="CC recipients")
    bcc: Optional[List[EmailStr]] = Field(None, description="BCC recipients")
    is_html: bool = Field(True, description="Whether body is HTML")
    reply_to: Optional[EmailStr] = Field(None, description="Reply-to address")
    attachments: Optional[List[str]] = Field(None, description="Attachment file paths")

    @model_validator(mode="after")
    def validate_content(self):
        if self.template_type:
            if not self.template_context:
                raise ValueError("template_context is required when template_type is provided")
        else:
            if not self.subject or not self.body:
                raise ValueError("subject and body are required when template_type is not provided")
        return self


class EmailResponse(BaseModel):
    """Response model for email sending operations."""

    success: bool = Field(..., description="Whether the email was sent successfully")
    message_id: Optional[str] = Field(None, description="Provider message ID if successful")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")


class ScheduledEmailRequest(BaseModel):
    """Request model for scheduling emails (combines email and schedule)."""

    email: EmailRequest = Field(..., description="Email request details")
    schedule: "ScheduleRequest" = Field(..., description="Schedule configuration")


from app.models.schedule import ScheduleRequest

ScheduledEmailRequest.model_rebuild()
