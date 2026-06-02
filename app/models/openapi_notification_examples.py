"""
OpenAPI / Swagger examples for email and push notification endpoints.
One example per template_type (plus direct/custom).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.templates.push_template_types import PushNotificationTemplateType
from app.templates.template_types import EmailTemplateType

# Shared sample data (notification matrix)
_SAMPLE = {
    "user_name": "Priya Sharma",
    "atp_name": "Kerala ATP Team",
    "host_name": "Rajesh Kumar",
    "guest_name": "Priya Sharma",
    "property_name": "Hill View Homestay",
    "location": "Munnar, Kerala",
    "area": "Idukki District",
    "checkin_date": "2026-06-15",
    "checkout_date": "2026-06-18",
    "check_in_date": "2026-06-15",
    "check_out_date": "2026-06-18",
    "amount": "4,500",
    "date": "2026-06-20",
    "otp": "739204",
    "otp_code": "482910",
    "expiry_minutes": 15,
    "booking_id": "BK-2026-00142",
    "issue": "Payment not reflected",
    "description": "Paid via UPI but booking still shows pending.",
    "issue_code": "TH-2026-0042",
    "notification_title": "Important Update",
    "message": "<p>You have a new notification from Triphavenco.</p>",
    "number_of_guests": "2",
    "total_amount": "₹12,500",
    "verification_link": "https://triphavenco.com/verify?token=example",
    "reset_link": "https://triphavenco.com/reset?token=example",
}

# template_type -> (summary prefix, description, context keys to include, recipient hint)
_EmailSpec = Tuple[str, str, List[str], str]

_EMAIL_SPECS: Dict[EmailTemplateType, _EmailSpec] = {
    EmailTemplateType.WELCOME: ("User", "Welcome new user", ["user_name"], "user"),
    EmailTemplateType.USER_REGISTRATION: ("User", "Registration invite", ["user_name", "verification_link"], "user"),
    EmailTemplateType.EMAIL_VERIFICATION: ("User", "Email verification OTP", ["user_name", "otp_code", "expiry_minutes"], "user"),
    EmailTemplateType.PASSWORD_RESET: ("Common", "Password reset OTP", ["user_name", "otp_code", "expiry_minutes"], "user"),
    EmailTemplateType.PASSWORD_CHANGED: ("User", "Password changed notice", ["user_name"], "user"),
    EmailTemplateType.ACCOUNT_ACTIVATED: ("User", "Account activated", ["user_name"], "user"),
    EmailTemplateType.ACCOUNT_DEACTIVATED: ("User", "Account deactivated", ["user_name"], "user"),
    EmailTemplateType.BOOKING_CONFIRMED: ("Booking", "Guest booking confirmed", ["guest_name", "property_name", "check_in_date", "check_out_date", "booking_id", "number_of_guests", "total_amount"], "user"),
    EmailTemplateType.BOOKING_CANCELLED: ("Booking", "Booking cancelled", ["guest_name", "property_name", "booking_id"], "user"),
    EmailTemplateType.BOOKING_REMINDER: ("Booking", "Upcoming stay reminder", ["guest_name", "property_name", "check_in_date"], "user"),
    EmailTemplateType.BOOKING_MODIFIED: ("Booking", "Booking modified", ["guest_name", "property_name", "check_in_date", "check_out_date", "booking_id"], "user"),
    EmailTemplateType.CHECK_IN_REMINDER: ("Booking", "Check-in reminder", ["guest_name", "property_name", "check_in_date"], "user"),
    EmailTemplateType.CHECK_OUT_REMINDER: ("Booking", "Check-out reminder", ["guest_name", "property_name", "check_out_date"], "user"),
    EmailTemplateType.PAYMENT_RECEIVED: ("Common", "Payment successful", ["user_name", "amount"], "user"),
    EmailTemplateType.PAYMENT_FAILED: ("Common", "Payment failed", ["user_name", "amount"], "user"),
    EmailTemplateType.PAYMENT_REMINDER: ("Common", "Payment reminder", ["user_name", "amount"], "user"),
    EmailTemplateType.INVOICE: ("Common", "Invoice", ["user_name", "amount", "booking_id"], "user"),
    EmailTemplateType.REVIEW_REQUEST: ("Booking", "Request guest review", ["guest_name", "property_name"], "user"),
    EmailTemplateType.REVIEW_RECEIVED: ("Host", "New review received", ["host_name", "guest_name", "property_name"], "host"),
    EmailTemplateType.NEW_BOOKING_REQUEST: ("Host", "New booking request", ["host_name", "guest_name", "property_name"], "host"),
    EmailTemplateType.BOOKING_APPROVED: ("Booking", "Booking approved", ["guest_name", "property_name", "booking_id"], "user"),
    EmailTemplateType.BOOKING_DECLINED: ("Booking", "Booking declined", ["guest_name", "property_name", "booking_id"], "user"),
    EmailTemplateType.HOST_REGISTRATION_ATP: ("ATP", "New host registration", ["atp_name", "host_name", "location"], "atp"),
    EmailTemplateType.HOST_REGISTRATION_SUBMITTED: ("Host", "Host application received", ["host_name"], "host"),
    EmailTemplateType.HOST_ACCOUNT_APPROVED: ("Host", "Host account approved", ["host_name"], "host"),
    EmailTemplateType.HOST_ACCOUNT_REJECTED: ("Host", "Host account rejected", ["host_name"], "host"),
    EmailTemplateType.HOST_ACCOUNT_SUSPENDED: ("Host", "Host account suspended", ["host_name"], "host"),
    EmailTemplateType.HOST_BOOKING_CANCELLED: ("Host", "Booking cancelled", ["host_name", "guest_name", "property_name"], "host"),
    EmailTemplateType.NEW_BOOKING_RECEIVED_HOST: ("Host", "New booking received", ["host_name", "guest_name", "property_name"], "host"),
    EmailTemplateType.GUEST_CHECK_IN_REMINDER_HOST: ("Host", "Guest arrival reminder", ["host_name", "guest_name", "checkin_date"], "host"),
    EmailTemplateType.PROPERTY_APPROVED: ("Host", "Property approved", ["host_name", "property_name"], "host"),
    EmailTemplateType.PROPERTY_REJECTED: ("Host", "Property rejected", ["host_name", "property_name"], "host"),
    EmailTemplateType.NEW_PROPERTY_SUBMITTED_ATP: ("ATP", "New property submitted", ["atp_name", "host_name", "property_name"], "atp"),
    EmailTemplateType.PROPERTY_UPDATED_ATP: ("ATP", "Property updated", ["atp_name", "host_name", "property_name"], "atp"),
    EmailTemplateType.NEW_BOOKING_ATP: ("ATP", "New booking alert", ["atp_name", "property_name", "guest_name", "checkin_date", "checkout_date"], "atp"),
    EmailTemplateType.GUEST_COMPLAINT_ATP: ("ATP", "Guest complaint", ["atp_name", "guest_name", "property_name"], "atp"),
    EmailTemplateType.HOST_SUSPENDED_ATP: ("ATP", "Host suspended notice", ["atp_name", "host_name"], "atp"),
    EmailTemplateType.ATP_REGISTRATION_SUBMITTED: ("ATP", "ATP application received", ["atp_name", "area"], "atp"),
    EmailTemplateType.ATP_APPROVED: ("ATP", "ATP account approved", ["atp_name"], "atp"),
    EmailTemplateType.ATP_REJECTED: ("ATP", "ATP application rejected", ["atp_name"], "atp"),
    EmailTemplateType.ATP_ACCOUNT_ACTIVATED: ("ATP", "ATP account activated", ["atp_name"], "atp"),
    EmailTemplateType.ATP_ACCOUNT_SUSPENDED: ("ATP", "ATP account suspended", ["atp_name"], "atp"),
    EmailTemplateType.ATP_ASSIGNED_AREA: ("ATP", "Area assigned", ["atp_name", "area"], "atp"),
    EmailTemplateType.OTP: ("Common", "OTP code", ["user_name", "otp"], "user"),
    EmailTemplateType.PASSWORD_RESET_SUCCESSFUL: ("Common", "Password reset successful", ["user_name"], "user"),
    EmailTemplateType.REFUND_ISSUED: ("Common", "Refund issued", ["user_name", "amount"], "user"),
    EmailTemplateType.NEW_OFFER: ("Common", "New promotional offer", ["user_name"], "user"),
    EmailTemplateType.GENERAL_NOTIFICATION: ("System", "Generic notification", ["user_name", "notification_title", "message"], "user"),
    EmailTemplateType.SYSTEM_ALERT: ("System", "System alert", ["user_name", "notification_title", "message"], "user"),
    EmailTemplateType.SUPPORT_CREATED: ("Support", "Support issue created", ["user_name", "issue", "description", "property_name", "issue_code"], "user"),
}

_PUSH_SPECS: Dict[PushNotificationTemplateType, _EmailSpec] = {
    PushNotificationTemplateType.HOST_REGISTRATION_ATP: ("ATP", "New host registration", ["host_name", "location"], "atp"),
    PushNotificationTemplateType.NEW_PROPERTY_SUBMITTED_ATP: ("ATP", "New property submitted", ["property_name"], "atp"),
    PushNotificationTemplateType.PROPERTY_UPDATED_ATP: ("ATP", "Property updated", ["property_name"], "atp"),
    PushNotificationTemplateType.NEW_BOOKING_ATP: ("ATP", "New booking alert", ["property_name", "guest_name"], "atp"),
    PushNotificationTemplateType.GUEST_COMPLAINT_ATP: ("ATP", "Guest complaint", ["property_name"], "atp"),
    PushNotificationTemplateType.HOST_SUSPENDED_ATP: ("ATP", "Host suspended", ["host_name"], "atp"),
    PushNotificationTemplateType.ATP_APPROVED: ("ATP", "ATP approved", [], "atp"),
    PushNotificationTemplateType.ATP_REJECTED: ("ATP", "ATP rejected", [], "atp"),
    PushNotificationTemplateType.ATP_ACCOUNT_ACTIVATED: ("ATP", "ATP activated", [], "atp"),
    PushNotificationTemplateType.ATP_ACCOUNT_SUSPENDED: ("ATP", "ATP suspended", [], "atp"),
    PushNotificationTemplateType.ATP_ASSIGNED_AREA: ("ATP", "Area assigned", ["area"], "atp"),
    PushNotificationTemplateType.HOST_ACCOUNT_APPROVED: ("Host", "Host approved", [], "host"),
    PushNotificationTemplateType.HOST_ACCOUNT_REJECTED: ("Host", "Host rejected", [], "host"),
    PushNotificationTemplateType.PROPERTY_APPROVED: ("Host", "Property live", ["property_name"], "host"),
    PushNotificationTemplateType.PROPERTY_REJECTED: ("Host", "Property rejected", ["property_name"], "host"),
    PushNotificationTemplateType.NEW_BOOKING_RECEIVED_HOST: ("Host", "New booking", ["property_name"], "host"),
    PushNotificationTemplateType.HOST_BOOKING_CANCELLED: ("Host", "Booking cancelled", ["property_name"], "host"),
    PushNotificationTemplateType.GUEST_CHECK_IN_REMINDER_HOST: ("Host", "Guest arriving", ["guest_name", "checkin_date"], "host"),
    PushNotificationTemplateType.REVIEW_RECEIVED: ("Host", "New review", ["guest_name"], "host"),
    PushNotificationTemplateType.HOST_ACCOUNT_SUSPENDED: ("Host", "Host suspended", [], "host"),
    PushNotificationTemplateType.MAINTENANCE_ALERT: ("Common", "Maintenance alert", ["date"], "user"),
    PushNotificationTemplateType.APP_UPDATE_AVAILABLE: ("Common", "App update", [], "user"),
    PushNotificationTemplateType.PASSWORD_RESET: ("Common", "Password reset request", [], "user"),
    PushNotificationTemplateType.PASSWORD_RESET_SUCCESSFUL: ("Common", "Password reset done", [], "user"),
    PushNotificationTemplateType.REFUND_ISSUED: ("Common", "Refund issued", ["amount"], "user"),
    PushNotificationTemplateType.PAYMENT_FAILED: ("Common", "Payment failed", ["amount"], "user"),
    PushNotificationTemplateType.PAYMENT_RECEIVED: ("Common", "Payment successful", ["amount"], "user"),
    PushNotificationTemplateType.NEW_OFFER: ("Common", "New offer", [], "user"),
}

_RECIPIENT_EMAIL = {
    "atp": "atp@example.com",
    "host": "host@example.com",
    "user": "user@example.com",
}

_USER_ID = {
    "atp": "atp-user-uuid",
    "host": "host-user-uuid",
    "user": "user-uuid",
}


def _context(keys: List[str]) -> Dict[str, Any]:
    return {k: _SAMPLE[k] for k in keys if k in _SAMPLE}


def _example_key(template_value: str) -> str:
    return template_value.lower()


def build_email_openapi_examples() -> Dict[str, Dict[str, Any]]:
    examples: Dict[str, Dict[str, Any]] = {}

    for template_type, (category, desc, keys, recipient) in _EMAIL_SPECS.items():
        key = _example_key(template_type.value)
        ctx = _context(keys)
        value: Dict[str, Any] = {
            "to": [_RECIPIENT_EMAIL[recipient]],
            "template_type": template_type.value,
            "template_context": ctx,
        }
        if template_type == EmailTemplateType.SUPPORT_CREATED:
            value["template_context"]["attachments"] = [
                "https://example.com/screenshot.png",
            ]

        examples[key] = {
            "summary": f"{category} — {template_type.value}",
            "description": desc,
            "value": value,
        }

    examples["direct_email"] = {
        "summary": "Direct email (no template)",
        "description": "Send raw HTML without a template. Requires subject and body.",
        "value": {
            "to": ["user@example.com"],
            "subject": "Custom Email Subject",
            "body": "<h1>Hello!</h1><p>This is a custom email body.</p>",
            "is_html": True,
        },
    }

    return examples


def build_push_openapi_examples() -> Dict[str, Dict[str, Any]]:
    examples: Dict[str, Dict[str, Any]] = {}

    for template_type, (category, desc, keys, recipient) in _PUSH_SPECS.items():
        key = _example_key(template_type.value)
        examples[key] = {
            "summary": f"{category} — {template_type.value}",
            "description": desc,
            "value": {
                "user_ids": [_USER_ID[recipient]],
                "template_type": template_type.value,
                "template_context": _context(keys),
                "data": {"event": template_type.value.lower()},
            },
        }

    examples["custom_push"] = {
        "summary": "Custom (no template)",
        "description": "Send with explicit headings and contents.",
        "value": {
            "player_ids": ["onesignal-player-id"],
            "headings": {"en": "Custom Title"},
            "contents": {"en": "Custom message body"},
            "data": {"type": "custom"},
            "priority": 10,
        },
    }

    return examples


def _validate_example_coverage() -> None:
    email_missing = set(EmailTemplateType) - set(_EMAIL_SPECS) - {EmailTemplateType.CUSTOM}
    push_missing = set(PushNotificationTemplateType) - set(_PUSH_SPECS)
    if email_missing:
        raise RuntimeError(
            "Missing email OpenAPI examples for: "
            + ", ".join(t.value for t in sorted(email_missing, key=lambda x: x.value))
        )
    if push_missing:
        raise RuntimeError(
            "Missing push OpenAPI examples for: "
            + ", ".join(t.value for t in sorted(push_missing, key=lambda x: x.value))
        )


_validate_example_coverage()

SEND_EMAIL_OPENAPI_EXAMPLES = build_email_openapi_examples()
SEND_PUSH_OPENAPI_EXAMPLES = build_push_openapi_examples()
