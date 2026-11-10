"""
Email template loader
Loads and renders email templates with variable substitution
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from app.templates.template_types import EmailTemplateType

# Get the templates directory path
TEMPLATES_DIR = Path(__file__).parent / "html"

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


class TemplateLoader:
    """Loads and renders email templates"""
    
    @staticmethod
    def render_template(
        template_type: EmailTemplateType,
        context: Dict[str, Any],
        custom_body: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Render an email template with the given context
        
        Args:
            template_type: The type of template to render
            context: Dictionary of variables to substitute in the template
            custom_body: Custom HTML body (used when template_type is CUSTOM)
            
        Returns:
            tuple: (subject, html_body)
        """
        if template_type == EmailTemplateType.CUSTOM:
            if not custom_body:
                raise ValueError("custom_body is required when using CUSTOM template type")
            # For custom templates, use the provided body and generate a subject
            subject = context.get("subject", "Notification from Heaven Connect")
            return subject, custom_body
        
        try:
            # Load the template file
            template_file = f"{template_type.value}.html"
            template = env.get_template(template_file)
            
            # Render the template with context
            html_body = template.render(**context)
            
            # Get subject from context or use default
            subject = context.get("subject") or TemplateLoader._get_default_subject(template_type)
            
            return subject, html_body
            
        except TemplateNotFound:
            raise ValueError(f"Template '{template_type.value}' not found")
        except Exception as e:
            raise ValueError(f"Error rendering template: {str(e)}")
    
    @staticmethod
    def _get_default_subject(template_type: EmailTemplateType) -> str:
        """Get default subject for a template type"""
        subjects = {
            EmailTemplateType.WELCOME: "Welcome to Heaven Connect!",
            EmailTemplateType.USER_REGISTRATION: "Welcome! Complete your registration",
            EmailTemplateType.EMAIL_VERIFICATION: "Verify your email address",
            EmailTemplateType.PASSWORD_RESET: "Reset your password",
            EmailTemplateType.PASSWORD_CHANGED: "Your password has been changed",
            EmailTemplateType.ACCOUNT_ACTIVATED: "Your account has been activated",
            EmailTemplateType.ACCOUNT_DEACTIVATED: "Your account has been deactivated",
            EmailTemplateType.BOOKING_CONFIRMED: "Booking Confirmed",
            EmailTemplateType.BOOKING_CANCELLED: "Booking Cancelled",
            EmailTemplateType.BOOKING_REMINDER: "Upcoming Booking Reminder",
            EmailTemplateType.BOOKING_MODIFIED: "Booking Modified",
            EmailTemplateType.CHECK_IN_REMINDER: "Check-in Reminder",
            EmailTemplateType.CHECK_OUT_REMINDER: "Check-out Reminder",
            EmailTemplateType.PAYMENT_RECEIVED: "Payment Received",
            EmailTemplateType.PAYMENT_FAILED: "Payment Failed",
            EmailTemplateType.PAYMENT_REMINDER: "Payment Reminder",
            EmailTemplateType.INVOICE: "Invoice",
            EmailTemplateType.REVIEW_REQUEST: "Share your experience",
            EmailTemplateType.REVIEW_RECEIVED: "New review received",
            EmailTemplateType.NEW_BOOKING_REQUEST: "New Booking Request",
            EmailTemplateType.BOOKING_APPROVED: "Booking Approved",
            EmailTemplateType.BOOKING_DECLINED: "Booking Declined",
            EmailTemplateType.GENERAL_NOTIFICATION: "Notification from Heaven Connect",
            EmailTemplateType.SYSTEM_ALERT: "System Alert",
            EmailTemplateType.HOST_REGISTRATION_ATP: "New Host Approval Required – Triphavenco",
            EmailTemplateType.NEW_PROPERTY_SUBMITTED_ATP: "Property Approval Required – Triphavenco",
            EmailTemplateType.PROPERTY_UPDATED_ATP: "Property Update Notification – Triphavenco",
            EmailTemplateType.NEW_BOOKING_ATP: "New Booking Notification– Triphavenco",
            EmailTemplateType.GUEST_COMPLAINT_ATP: "Guest /Host Complaint Notification – Triphavenco",
            EmailTemplateType.HOST_SUSPENDED_ATP: "Host Account Suspension Notice – Triphavenco",
            EmailTemplateType.ATP_REGISTRATION_SUBMITTED: "ATP Application Received – Triphavenco",
            EmailTemplateType.ATP_APPROVED: "ATP Account Approved – Triphavenco",
            EmailTemplateType.ATP_REJECTED: "ATP Application Status – Triphavenco",
            EmailTemplateType.ATP_ACCOUNT_ACTIVATED: "ATP Account Activated – Triphavenco",
            EmailTemplateType.ATP_ACCOUNT_SUSPENDED: "ATP Account Suspended – Triphavenco",
            EmailTemplateType.ATP_ASSIGNED_AREA: "Area Assignment – Triphavenco",
            EmailTemplateType.HOST_REGISTRATION_SUBMITTED: "Host Application Received – Triphavenco",
            EmailTemplateType.HOST_ACCOUNT_APPROVED: "Host Account Approved – Triphavenco",
            EmailTemplateType.HOST_ACCOUNT_REJECTED: "Host Application Status – Triphavenco",
            EmailTemplateType.PROPERTY_APPROVED: "Property Approved – Triphavenco",
            EmailTemplateType.PROPERTY_REJECTED: "Property Rejected – Triphavenco",
            EmailTemplateType.NEW_BOOKING_RECEIVED_HOST: "New Booking Received – Triphavenco",
            EmailTemplateType.HOST_BOOKING_CANCELLED: "Booking Cancelled – Triphavenco",
            EmailTemplateType.GUEST_CHECK_IN_REMINDER_HOST: "Guest Arrival Reminder – Triphavenco",
            EmailTemplateType.REVIEW_RECEIVED: "New Review Received – Triphavenco",
            EmailTemplateType.HOST_ACCOUNT_SUSPENDED: "Host Account Suspended – Triphavenco",
            EmailTemplateType.OTP: "Your Triphavenco OTP Code",
            EmailTemplateType.LOGIN: "Your Triphavenco login code",
            EmailTemplateType.PASSWORD_RESET_SUCCESSFUL: "Password Reset Successful",
            EmailTemplateType.REFUND_ISSUED: "Refund Issued – Triphavenco",
            EmailTemplateType.PAYMENT_FAILED: "Payment Failed – Triphavenco",
            EmailTemplateType.PAYMENT_RECEIVED: "Payment Successful – Triphavenco",
            EmailTemplateType.NEW_OFFER: "New Offer – Triphavenco",
            EmailTemplateType.SUPPORT_CREATED: "Support Issue Created – Triphavenco",
            EmailTemplateType.PASSWORD_RESET: "Password Reset Request – Triphavenco",
        }
        return subjects.get(template_type, "Notification from Triphavenco")

