"""
Email request and response models
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.openapi_notification_examples import SEND_EMAIL_OPENAPI_EXAMPLES
from app.templates.template_types import EmailTemplateType


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
    area: Optional[str] = Field(None, description="ATP assigned area")
    amount: Optional[str] = Field(None, description="Payment or refund amount")
    checkin_date: Optional[str] = Field(None, description="Check-in date (alias: check_in_date)")
    checkout_date: Optional[str] = Field(None, description="Check-out date (alias: check_out_date)")
    otp: Optional[str] = Field(None, description="OTP code (alias: otp_code)")

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
    template_type: Optional[EmailTemplateType] = Field(
        None,
        description=(
            "Triphavenco HTML template identifier (file: app/templates/html/{value}.html). "
            "Use with template_context. Omit to send subject/body directly."
        ),
    )
    template_context: Optional[EmailTemplateContext] = Field(
        None,
        description=(
            "Variables substituted into the template (Jinja2). "
            "Common fields: user_name, atp_name, host_name, guest_name, property_name, location, area, "
            "checkin_date, checkout_date, check_in_date, check_out_date, amount, otp, otp_code, "
            "issue, description, issue_code. Optional subject overrides the default."
        ),
    )

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
