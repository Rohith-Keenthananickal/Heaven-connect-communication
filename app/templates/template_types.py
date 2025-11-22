"""
Email template types enum
Defines all available email templates
"""

from enum import Enum


class EmailTemplateType(str, Enum):
    """Enumeration of available email templates"""
    
    # User-related templates
    WELCOME = "welcome"
    USER_REGISTRATION = "user_registration"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    PASSWORD_CHANGED = "password_changed"
    ACCOUNT_ACTIVATED = "account_activated"
    ACCOUNT_DEACTIVATED = "account_deactivated"
    
    # Booking-related templates (Airbnb-like)
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_REMINDER = "booking_reminder"
    BOOKING_MODIFIED = "booking_modified"
    CHECK_IN_REMINDER = "check_in_reminder"
    CHECK_OUT_REMINDER = "check_out_reminder"
    
    # Payment-related templates
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REMINDER = "payment_reminder"
    INVOICE = "invoice"
    
    # Review-related templates
    REVIEW_REQUEST = "review_request"
    REVIEW_RECEIVED = "review_received"
    
    # Host-related templates
    NEW_BOOKING_REQUEST = "new_booking_request"
    BOOKING_APPROVED = "booking_approved"
    BOOKING_DECLINED = "booking_declined"
    
    # Notification templates
    GENERAL_NOTIFICATION = "general_notification"
    SYSTEM_ALERT = "system_alert"
    
    # Custom template (for when user provides their own content)
    CUSTOM = "custom"

