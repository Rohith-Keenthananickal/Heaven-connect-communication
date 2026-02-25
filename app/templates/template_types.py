"""
Email template types enum
Defines all available email templates
"""

from enum import Enum


class EmailTemplateType(str, Enum):
    """Enumeration of available email templates"""
    
    # User-related templates
    WELCOME = "WELCOME"
    USER_REGISTRATION = "USER_REGISTRATION"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    ACCOUNT_ACTIVATED = "ACCOUNT_ACTIVATED"
    ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
    
    # Booking-related templates (Airbnb-like)
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    BOOKING_REMINDER = "BOOKING_REMINDER"
    BOOKING_MODIFIED = "BOOKING_MODIFIED"
    CHECK_IN_REMINDER = "CHECK_IN_REMINDER"
    CHECK_OUT_REMINDER = "CHECK_OUT_REMINDER"
    
    # Payment-related templates
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_REMINDER = "PAYMENT_REMINDER"
    INVOICE = "INVOICE"
    
    # Review-related templates
    REVIEW_REQUEST = "REVIEW_REQUEST"
    REVIEW_RECEIVED = "REVIEW_RECEIVED"
    
    # Host-related templates
    NEW_BOOKING_REQUEST = "NEW_BOOKING_REQUEST"
    BOOKING_APPROVED = "BOOKING_APPROVED"
    BOOKING_DECLINED = "BOOKING_DECLINED"
    
    # Notification templates
    GENERAL_NOTIFICATION = "GENERAL_NOTIFICATION"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    
    # Custom template (for when user provides their own content)
    CUSTOM = "CUSTOM"

