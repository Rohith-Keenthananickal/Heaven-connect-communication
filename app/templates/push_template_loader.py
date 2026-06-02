"""
Push notification template loader — title and message from the Triphavenco matrix.
"""

from typing import Any, Dict, Tuple

from jinja2 import BaseLoader, Environment, TemplateNotFound, select_autoescape

from app.templates.push_template_types import PushNotificationTemplateType

_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Push Title | Push Message (Google Sheet — Notifications tab)
_PUSH_TEMPLATES: Dict[PushNotificationTemplateType, Dict[str, str]] = {
    PushNotificationTemplateType.HOST_REGISTRATION_ATP: {
        "title": "New Host Registration",
        "message": "{{ host_name }} registered in {{ location }}. Approval required.",
    },
    PushNotificationTemplateType.NEW_PROPERTY_SUBMITTED_ATP: {
        "title": "New Property Submitted",
        "message": "{{ property_name }} submitted for approval.",
    },
    PushNotificationTemplateType.PROPERTY_UPDATED_ATP: {
        "title": "Property Update Alert",
        "message": "{{ property_name }} updated. Review required.",
    },
    PushNotificationTemplateType.NEW_BOOKING_ATP: {
        "title": "New Booking Alert",
        "message": "New booking at {{ property_name }} by {{ guest_name }}.",
    },
    PushNotificationTemplateType.GUEST_COMPLAINT_ATP: {
        "title": "Guest Complaint Alert",
        "message": "Complaint raised for {{ property_name }}.",
    },
    PushNotificationTemplateType.HOST_SUSPENDED_ATP: {
        "title": "Host Account Suspended",
        "message": "{{ host_name }} account suspended.",
    },
    PushNotificationTemplateType.ATP_APPROVED: {
        "title": "Congratulation",
        "message": "Your ATP account is approved.",
    },
    PushNotificationTemplateType.ATP_REJECTED: {
        "title": "Application Update",
        "message": "Your ATP application was not approved.",
    },
    PushNotificationTemplateType.ATP_ACCOUNT_ACTIVATED: {
        "title": "Account Activated",
        "message": "Your ATP account is now active.",
    },
    PushNotificationTemplateType.ATP_ACCOUNT_SUSPENDED: {
        "title": "Account Suspended",
        "message": "Your ATP account has been suspended.",
    },
    PushNotificationTemplateType.ATP_ASSIGNED_AREA: {
        "title": "Area Assigned",
        "message": "You are assigned to manage {{ area }}.",
    },
    PushNotificationTemplateType.HOST_ACCOUNT_APPROVED: {
        "title": "Account Approved",
        "message": "Your host account is approved. You can now list properties.",
    },
    PushNotificationTemplateType.HOST_ACCOUNT_REJECTED: {
        "title": "Account Not Approved",
        "message": "Your host account was not approved.",
    },
    PushNotificationTemplateType.PROPERTY_APPROVED: {
        "title": "Property Approved",
        "message": "{{ property_name }} is now live.",
    },
    PushNotificationTemplateType.PROPERTY_REJECTED: {
        "title": "Property Rejected",
        "message": "{{ property_name }} was not approved.",
    },
    PushNotificationTemplateType.NEW_BOOKING_RECEIVED_HOST: {
        "title": "New Booking",
        "message": "You received booking for {{ property_name }}.",
    },
    PushNotificationTemplateType.HOST_BOOKING_CANCELLED: {
        "title": "Booking Cancelled",
        "message": "Booking for {{ property_name }} was cancelled.",
    },
    PushNotificationTemplateType.GUEST_CHECK_IN_REMINDER_HOST: {
        "title": "Guest Arriving Soon",
        "message": "{{ guest_name }} arriving on {{ checkin_date | default(check_in_date) }}.",
    },
    PushNotificationTemplateType.REVIEW_RECEIVED: {
        "title": "New Review",
        "message": "{{ guest_name }} reviewed your property.",
    },
    PushNotificationTemplateType.HOST_ACCOUNT_SUSPENDED: {
        "title": "Account Suspended",
        "message": "Your host account has been suspended.",
    },
    PushNotificationTemplateType.MAINTENANCE_ALERT: {
        "title": "Maintenance Alert",
        "message": "Triphavenco will be under maintenance on {{ date }}.",
    },
    PushNotificationTemplateType.APP_UPDATE_AVAILABLE: {
        "title": "Update Available",
        "message": "New version of Triphavenco is available. Please update.",
    },
    PushNotificationTemplateType.PASSWORD_RESET: {
        "title": "Password Reset Request",
        "message": "Reset your password using OTP.",
    },
    PushNotificationTemplateType.PASSWORD_RESET_SUCCESSFUL: {
        "title": "Password Reset",
        "message": "Your password was reset successfully.",
    },
    PushNotificationTemplateType.REFUND_ISSUED: {
        "title": "Refund Issued",
        "message": "₹{{ amount }} refund issued.",
    },
    PushNotificationTemplateType.PAYMENT_FAILED: {
        "title": "Payment Failed",
        "message": "Your payment of ₹{{ amount }} failed.",
    },
    PushNotificationTemplateType.PAYMENT_RECEIVED: {
        "title": "Payment Successful",
        "message": "Your payment of ₹{{ amount }} successful.",
    },
    PushNotificationTemplateType.NEW_OFFER: {
        "title": "New Offer",
        "message": "New offer available on Triphavenco.",
    },
}


class PushTemplateLoader:
    """Renders push title and body from predefined templates."""

    @staticmethod
    def render_template(
        template_type: PushNotificationTemplateType,
        context: Dict[str, Any],
        language: str = "en",
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        spec = _PUSH_TEMPLATES.get(template_type)
        if not spec:
            raise TemplateNotFound(str(template_type))

        title = _env.from_string(spec["title"]).render(**context)
        message = _env.from_string(spec["message"]).render(**context)

        return {language: title}, {language: message}

    @staticmethod
    def list_templates() -> Dict[str, Dict[str, str]]:
        """Return static title/message patterns for documentation."""
        return {
            t.value: {"title": spec["title"], "message": spec["message"]}
            for t, spec in _PUSH_TEMPLATES.items()
        }
