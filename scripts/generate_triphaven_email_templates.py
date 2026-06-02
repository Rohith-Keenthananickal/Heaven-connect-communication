#!/usr/bin/env python3
"""One-off generator for Triphavenco-styled email HTML templates."""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "app" / "templates" / "html"

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - Triphavenco</title>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@400;500;600;700&display=swap');
    </style>
</head>
<body style="margin:0;padding:0;background-color:#E9F6F7;font-family:'Manrope',Arial,sans-serif;">
"""

FOOTER = """
                <tr>
                    <td style="background-color:#1F1F1F;border-radius:0 0 20px 20px;padding:28px 48px;">
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:20px;">
                            <tr>
                                <td width="40" style="background:#FFD26E;height:2px;border-radius:2px;font-size:0;">&nbsp;</td>
                                <td style="font-size:0;">&nbsp;</td>
                            </tr>
                        </table>
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                                <td style="vertical-align:top;">
                                    <p style="margin:0 0 6px;font-size:12px;color:rgba(255,255,255,0.45);font-family:'Manrope',Arial,sans-serif;">Need help? Reach us at</p>
                                    <a href="mailto:support@triphavenco.com" style="font-size:13px;color:#2BB0B8;text-decoration:none;font-weight:600;font-family:'Manrope',Arial,sans-serif;">support@triphavenco.com</a>
                                </td>
                                <td style="text-align:right;vertical-align:top;">
                                    <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.25);font-family:'Manrope',Arial,sans-serif;">
                                        &copy; {{ current_year | default('2026') }} Triphavenco<br>All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                        <p style="margin:20px 0 0;font-size:11px;color:rgba(255,255,255,0.2);text-align:center;letter-spacing:1px;font-family:'Sora',Arial,sans-serif;text-transform:uppercase;">Experience Authentic Homestays · Kerala's Rich Culture</p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</body>
</html>
"""


def detail_rows(rows: list[tuple[str, str]]) -> str:
    parts = []
    for label, var in rows:
        parts.append(
            f"""                                                    <tr>
                                                        <td style="padding:8px 0;font-size:14px;color:#4A5568;font-family:'Manrope',Arial,sans-serif;line-height:1.6;">
                                                            <strong style="color:#1A8491;">{label}:</strong> {{{{ {var} | default('N/A') }}}}
                                                        </td>
                                                    </tr>"""
        )
    return "\n".join(parts)


def render(
    *,
    filename: str,
    page_title: str,
    header_title: str,
    header_subtitle: str,
    greeting_var: str,
    greeting_default: str,
    greeting_prefix: str = "Dear",
    body_html: str,
    details_title: str = "Details",
    details: list[tuple[str, str]] | None = None,
    instruction_emoji: str | None = None,
    instruction_text: str | None = None,
    otp_block: bool = False,
    otp_var: str = "otp",
) -> None:
    if greeting_prefix == "Dear":
        greeting_line = (
            f'Dear <span style="color:#1A8491;">{{{{ {greeting_var} | default(\'{greeting_default}\') }}}}</span>,'
        )
    else:
        greeting_line = (
            f'Hello, <span style="color:#1A8491;">{{{{ {greeting_var} | default(\'{greeting_default}\') }}}}</span> 👋'
        )
    greeting = f"""                        <p style="margin:0 0 18px;font-size:16px;color:#1F1F1F;font-weight:600;font-family:'Manrope',Arial,sans-serif;">
                            {greeting_line}
                        </p>"""

    details_section = ""
    if details:
        details_section = f"""
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
                            <tr>
                                <td>
                                    <table role="presentation" cellpadding="0" cellspacing="0" width="100%"
                                           style="border-radius:16px;overflow:hidden;border:1.5px solid #D6F0F2;">
                                        <tr>
                                            <td width="6" style="background:linear-gradient(180deg,#2BB0B8,#1A8491);font-size:0;">&nbsp;</td>
                                            <td style="background:#F0FBFC;padding:28px 32px;">
                                                <p style="margin:0 0 16px;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#1A8491;font-weight:700;font-family:'Manrope',Arial,sans-serif;">{details_title}</p>
                                                <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
{detail_rows(details)}
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>"""

    otp_section = ""
    if otp_block:
        otp_section = f"""
                        {{% if {otp_var} or otp_code %}}
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
                            <tr>
                                <td>
                                    <table role="presentation" cellpadding="0" cellspacing="0" width="100%"
                                           style="border-radius:16px;overflow:hidden;border:1.5px solid #D6F0F2;">
                                        <tr>
                                            <td width="6" style="background:linear-gradient(180deg,#2BB0B8,#1A8491);font-size:0;">&nbsp;</td>
                                            <td style="background:#F0FBFC;padding:28px 32px;text-align:center;">
                                                <p style="margin:0 0 6px;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#1A8491;font-weight:700;font-family:'Manrope',Arial,sans-serif;">Your OTP Code</p>
                                                <p style="margin:0 0 16px;font-size:13px;color:#718096;font-family:'Manrope',Arial,sans-serif;">Do not share this code with anyone</p>
                                                <table role="presentation" cellpadding="0" cellspacing="0" align="center">
                                                    <tr>
                                                        <td style="background:#FFD26E;border-radius:12px;padding:14px 28px;">
                                                            <p style="margin:0;font-family:'Sora','Courier New',monospace;font-size:32px;font-weight:700;color:#1F1F1F;letter-spacing:6px;">{{{{ {otp_var} | default(otp_code) | default('N/A') }}}}</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                        {{% endif %}}"""

    instruction_section = ""
    if instruction_emoji and instruction_text:
        instruction_section = f"""
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:28px;">
                            <tr>
                                <td style="background:#F8FAFB;border-radius:12px;padding:18px 22px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td style="font-size:20px;vertical-align:middle;padding-right:14px;">{instruction_emoji}</td>
                                            <td style="font-size:14px;color:#4A5568;line-height:1.7;font-family:'Manrope',Arial,sans-serif;vertical-align:middle;">
                                                {instruction_text}
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>"""

    html = (
        HEAD.format(page_title=page_title)
        + """
<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color:#E9F6F7;padding:40px 16px;">
    <tr>
        <td align="center">
            <table role="presentation" cellpadding="0" cellspacing="0" width="600" style="max-width:600px;width:100%;">
                <tr>
                    <td style="background:linear-gradient(135deg,#2BB0B8 0%,#1A8491 100%);border-radius:20px 20px 0 0;padding:0;overflow:hidden;">
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                            <tr><td style="background-color:#FFD26E;height:4px;font-size:0;line-height:0;">&nbsp;</td></tr>
                        </table>
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                                <td style="padding:36px 40px 32px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td style="background:#ffffff;border-radius:14px;padding:10px 12px;vertical-align:middle;">
                                                <img src="https://admin.triphavenco.com/Triphaven-logo.png" alt="Triphavenco logo" width="44" height="44" style="display:block;">
                                            </td>
                                            <td style="padding-left:16px;vertical-align:middle;">
                                                <p style="margin:0 0 2px;font-family:'Sora',Arial,sans-serif;font-size:20px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;">Triphavenco</p>
                                                <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.75);letter-spacing:0.5px;font-weight:500;">Experience authentic homestays</p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                                <td width="120" style="vertical-align:bottom;padding-right:32px;padding-bottom:0;text-align:right;">
                                    <div style="width:100px;height:100px;border-radius:50%;background:rgba(255,255,255,0.08);display:inline-block;margin-bottom:-2px;position:relative;">
                                        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:64px;height:64px;border-radius:50%;border:2px solid rgba(255,210,110,0.35);"></div>
                                    </div>
                                </td>
                            </tr>
                        </table>
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                                <td style="background:rgba(0,0,0,0.12);padding:20px 40px 28px;text-align:center;">
                                    <h1 style="margin:0 0 6px;font-family:'Manrope',Arial,sans-serif;font-size:26px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">"""
        + header_title
        + """</h1>
                                    <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.75);font-weight:500;letter-spacing:0.3px;">"""
        + header_subtitle
        + """</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td style="background-color:#ffffff;padding:44px 48px 36px;">
"""
        + greeting
        + f"""
                        <p style="margin:0 0 32px;font-size:15px;line-height:1.8;color:#4A5568;font-family:'Manrope',Arial,sans-serif;font-weight:400;">
                            {body_html}
                        </p>
"""
        + details_section
        + otp_section
        + instruction_section
        + """
                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:24px;">
                            <tr><td style="border-top:1px solid #EDF2F7;font-size:0;">&nbsp;</td></tr>
                        </table>
                        <p style="margin:0 0 28px;font-size:13px;color:#A0AEC0;line-height:1.7;font-family:'Manrope',Arial,sans-serif;">
                            💬 &nbsp;Questions? Email us at <a href="mailto:support@triphavenco.com" style="color:#1A8491;text-decoration:none;font-weight:600;">support@triphavenco.com</a>.
                        </p>
                        <p style="margin:0;font-size:15px;color:#1F1F1F;font-family:'Manrope',Arial,sans-serif;">
                            Warm regards,<br>
                            <strong style="color:#1A8491;font-size:16px;">Team Triphavenco</strong>
                        </p>
                    </td>
                </tr>
"""
        + FOOTER
    )

    path = OUT / f"{filename}.html"
    path.write_text(html, encoding="utf-8")
    print(f"Wrote {path.name}")


TEMPLATES = [
    # ATP
    dict(
        filename="NEW_PROPERTY_SUBMITTED_ATP",
        page_title="Property Approval Required",
        header_title="New Property Submitted",
        header_subtitle="A property is awaiting your approval",
        greeting_var="atp_name",
        greeting_default="ATP Team",
        body_html="Property <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong> has been submitted by <strong style=\"color:#1A8491;\">{{ host_name | default('N/A') }}</strong>. Please review and approve.",
        details_title="Property Details",
        details=[("Property", "property_name"), ("Host", "host_name")],
        instruction_emoji="✅",
        instruction_text="Please log in to the <strong style=\"color:#1A8491;\">ATP portal</strong> to review and approve this property.",
    ),
    dict(
        filename="PROPERTY_UPDATED_ATP",
        page_title="Property Update Notification",
        header_title="Property Update Alert",
        header_subtitle="A property has been updated and needs review",
        greeting_var="atp_name",
        greeting_default="ATP Team",
        body_html="Property <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong> was updated by <strong style=\"color:#1A8491;\">{{ host_name | default('N/A') }}</strong>. Please review the changes.",
        details_title="Update Details",
        details=[("Property", "property_name"), ("Host", "host_name")],
        instruction_emoji="📋",
        instruction_text="Please log in to the <strong style=\"color:#1A8491;\">ATP portal</strong> to review the updated property details.",
    ),
    dict(
        filename="NEW_BOOKING_ATP",
        page_title="New Booking Notification",
        header_title="New Booking Alert",
        header_subtitle="A new booking requires your attention",
        greeting_var="atp_name",
        greeting_default="ATP Team",
        body_html="A new booking at <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong> by <strong style=\"color:#1A8491;\">{{ guest_name | default('N/A') }}</strong> from {{ checkin_date | default(check_in_date) | default('N/A') }} to {{ checkout_date | default(check_out_date) | default('N/A') }}.",
        details_title="Booking Details",
        details=[
            ("Property", "property_name"),
            ("Guest", "guest_name"),
            ("Check-in", "checkin_date"),
            ("Check-out", "checkout_date"),
        ],
        instruction_emoji="📅",
        instruction_text="Please log in to the <strong style=\"color:#1A8491;\">ATP portal</strong> to view full booking details.",
    ),
    dict(
        filename="GUEST_COMPLAINT_ATP",
        page_title="Guest Complaint Notification",
        header_title="Guest Complaint Alert",
        header_subtitle="A complaint requires your attention",
        greeting_var="atp_name",
        greeting_default="ATP Team",
        body_html="A complaint from <strong style=\"color:#1A8491;\">{{ guest_name | default('N/A') }}</strong> for <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong>. Please take action.",
        details_title="Complaint Details",
        details=[("Guest", "guest_name"), ("Property", "property_name")],
        instruction_emoji="⚠️",
        instruction_text="Please log in to the <strong style=\"color:#1A8491;\">ATP portal</strong> to investigate and resolve this complaint.",
    ),
    dict(
        filename="HOST_SUSPENDED_ATP",
        page_title="Host Account Suspension Notice",
        header_title="Host Account Suspended",
        header_subtitle="A host account has been suspended",
        greeting_var="atp_name",
        greeting_default="ATP Team",
        body_html="Host <strong style=\"color:#1A8491;\">{{ host_name | default('N/A') }}</strong> has been suspended due to a policy violation.",
        details_title="Host Details",
        details=[("Host", "host_name")],
        instruction_emoji="ℹ️",
        instruction_text="This is an informational notice for your records. No action is required unless you need to follow up.",
    ),
    dict(
        filename="ATP_REGISTRATION_SUBMITTED",
        page_title="ATP Application Received",
        header_title="Application Received",
        header_subtitle="Your ATP application is being reviewed",
        greeting_var="atp_name",
        greeting_default="Applicant",
        body_html="Your ATP application for <strong style=\"color:#1A8491;\">{{ area | default('N/A') }}</strong> has been received. Approval is in progress.",
        details_title="Application Details",
        details=[("Area", "area")],
        instruction_emoji="⏳",
        instruction_text="We will notify you once your application has been reviewed. Thank you for your patience.",
    ),
    dict(
        filename="ATP_APPROVED",
        page_title="ATP Account Approved",
        header_title="Congratulations!",
        header_subtitle="Your ATP account has been approved",
        greeting_var="atp_name",
        greeting_default="ATP",
        body_html="Your ATP account is approved. You can now log in and manage your area.",
        instruction_emoji="🎉",
        instruction_text="Log in to the <strong style=\"color:#1A8491;\">ATP portal</strong> to get started.",
    ),
    dict(
        filename="ATP_REJECTED",
        page_title="ATP Application Status",
        header_title="Application Update",
        header_subtitle="Your ATP application was not approved",
        greeting_var="atp_name",
        greeting_default="Applicant",
        body_html="Your ATP application was not approved. Please contact support for more information.",
        instruction_emoji="📞",
        instruction_text="Contact us at <a href=\"mailto:support@triphavenco.com\" style=\"color:#1A8491;text-decoration:none;font-weight:600;\">support@triphavenco.com</a> if you have questions.",
    ),
    dict(
        filename="ATP_ACCOUNT_ACTIVATED",
        page_title="ATP Account Activated",
        header_title="Account Activated",
        header_subtitle="Your ATP account is now active",
        greeting_var="atp_name",
        greeting_default="ATP",
        body_html="Your ATP account is now active and ready to use.",
        instruction_emoji="✅",
        instruction_text="Log in to the <strong style=\"color:#1A8491;\">ATP portal</strong> to access your dashboard.",
    ),
    dict(
        filename="ATP_ACCOUNT_SUSPENDED",
        page_title="ATP Account Suspended",
        header_title="Account Suspended",
        header_subtitle="Your ATP account has been suspended",
        greeting_var="atp_name",
        greeting_default="ATP",
        body_html="Your ATP account has been suspended due to a policy violation.",
        instruction_emoji="📞",
        instruction_text="Please contact <a href=\"mailto:support@triphavenco.com\" style=\"color:#1A8491;text-decoration:none;font-weight:600;\">support@triphavenco.com</a> for assistance.",
    ),
    dict(
        filename="ATP_ASSIGNED_AREA",
        page_title="Area Assignment",
        header_title="Area Assigned",
        header_subtitle="You have been assigned a new area",
        greeting_var="atp_name",
        greeting_default="ATP",
        body_html="You are now Area Tourism Promoter for <strong style=\"color:#1A8491;\">{{ area | default('N/A') }}</strong>.",
        details_title="Assignment Details",
        details=[("Area", "area")],
        instruction_emoji="🗺️",
        instruction_text="Log in to the <strong style=\"color:#1A8491;\">ATP portal</strong> to manage your assigned area.",
    ),
    # Host
    dict(
        filename="HOST_REGISTRATION_SUBMITTED",
        page_title="Host Application Received",
        header_title="Application Received",
        header_subtitle="Your host application is being reviewed",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="Your host application has been received. We will review it and notify you soon.",
        instruction_emoji="⏳",
        instruction_text="You will receive another email once your application has been reviewed.",
    ),
    dict(
        filename="HOST_ACCOUNT_APPROVED",
        page_title="Host Account Approved",
        header_title="Account Approved",
        header_subtitle="Your host account is ready",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="Congratulations! Your host account is approved. You can now list properties on Triphavenco.",
        instruction_emoji="🏠",
        instruction_text="Log in to your <strong style=\"color:#1A8491;\">host dashboard</strong> to add your first property.",
    ),
    dict(
        filename="HOST_ACCOUNT_REJECTED",
        page_title="Host Application Status",
        header_title="Account Not Approved",
        header_subtitle="Your host application was not approved",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="Your host account application was not approved. Please contact support for more information.",
        instruction_emoji="📞",
        instruction_text="Contact us at <a href=\"mailto:support@triphavenco.com\" style=\"color:#1A8491;text-decoration:none;font-weight:600;\">support@triphavenco.com</a> if you have questions.",
    ),
    dict(
        filename="PROPERTY_APPROVED",
        page_title="Property Approved",
        header_title="Property Approved",
        header_subtitle="Your property is now live",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="Your property <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong> is approved and live on Triphavenco.",
        details_title="Property Details",
        details=[("Property", "property_name")],
        instruction_emoji="🎉",
        instruction_text="Guests can now discover and book your property.",
    ),
    dict(
        filename="PROPERTY_REJECTED",
        page_title="Property Rejected",
        header_title="Property Rejected",
        header_subtitle="Your property was not approved",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="Your property <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong> was not approved. Please update and resubmit.",
        details_title="Property Details",
        details=[("Property", "property_name")],
        instruction_emoji="📝",
        instruction_text="Log in to your <strong style=\"color:#1A8491;\">host dashboard</strong> to update your listing and resubmit for approval.",
    ),
    dict(
        filename="NEW_BOOKING_RECEIVED_HOST",
        page_title="New Booking Received",
        header_title="New Booking",
        header_subtitle="You received a new booking",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="You received a booking from <strong style=\"color:#1A8491;\">{{ guest_name | default('N/A') }}</strong> for <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong>.",
        details_title="Booking Details",
        details=[("Guest", "guest_name"), ("Property", "property_name")],
        instruction_emoji="📅",
        instruction_text="Log in to your <strong style=\"color:#1A8491;\">host dashboard</strong> to view booking details.",
    ),
    dict(
        filename="HOST_BOOKING_CANCELLED",
        page_title="Booking Cancelled",
        header_title="Booking Cancelled",
        header_subtitle="A booking for your property was cancelled",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="Booking from <strong style=\"color:#1A8491;\">{{ guest_name | default('N/A') }}</strong> for <strong style=\"color:#1A8491;\">{{ property_name | default('N/A') }}</strong> was cancelled.",
        details_title="Booking Details",
        details=[("Guest", "guest_name"), ("Property", "property_name")],
    ),
    dict(
        filename="GUEST_CHECK_IN_REMINDER_HOST",
        page_title="Guest Arrival Reminder",
        header_title="Guest Arriving Soon",
        header_subtitle="Prepare for your guest's arrival",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="<strong style=\"color:#1A8491;\">{{ guest_name | default('N/A') }}</strong> will check in on <strong style=\"color:#1A8491;\">{{ checkin_date | default(check_in_date) | default('N/A') }}</strong>.",
        details_title="Arrival Details",
        details=[("Guest", "guest_name"), ("Check-in", "checkin_date")],
        instruction_emoji="🏡",
        instruction_text="Please ensure your property is ready for the guest's arrival.",
    ),
    dict(
        filename="REVIEW_RECEIVED",
        page_title="New Review Received",
        header_title="New Review",
        header_subtitle="A guest reviewed your property",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="You received a review from <strong style=\"color:#1A8491;\">{{ guest_name | default('N/A') }}</strong>.",
        details_title="Review Details",
        details=[("Guest", "guest_name"), ("Property", "property_name")],
        instruction_emoji="⭐",
        instruction_text="Log in to your <strong style=\"color:#1A8491;\">host dashboard</strong> to read and respond to the review.",
    ),
    dict(
        filename="HOST_ACCOUNT_SUSPENDED",
        page_title="Host Account Suspended",
        header_title="Account Suspended",
        header_subtitle="Your host account has been suspended",
        greeting_var="host_name",
        greeting_default="Host",
        body_html="Your account has been suspended due to a policy violation.",
        instruction_emoji="📞",
        instruction_text="Please contact <a href=\"mailto:support@triphavenco.com\" style=\"color:#1A8491;text-decoration:none;font-weight:600;\">support@triphavenco.com</a> for assistance.",
    ),
    # Common
    dict(
        filename="OTP",
        page_title="Your OTP Code",
        header_title="Your OTP Code",
        header_subtitle="Use this code to verify your identity",
        greeting_var="user_name",
        greeting_default="User",
        greeting_prefix="Dear",
        body_html="Your One-Time Passcode (OTP) is below. Do not share it with anyone.",
        otp_block=True,
        instruction_emoji="🔒",
        instruction_text="This code is valid for a limited time. If you did not request this, please ignore this email.",
    ),
    dict(
        filename="PASSWORD_RESET_SUCCESSFUL",
        page_title="Password Reset Successful",
        header_title="Password Reset",
        header_subtitle="Your password was reset successfully",
        greeting_var="user_name",
        greeting_default="User",
        greeting_prefix="Dear",
        body_html="Your password has been reset successfully. You can now log in with your new password.",
        instruction_emoji="🔑",
        instruction_text="If you did not reset your password, contact us immediately at <a href=\"mailto:support@triphavenco.com\" style=\"color:#1A8491;text-decoration:none;font-weight:600;\">support@triphavenco.com</a>.",
    ),
    dict(
        filename="REFUND_ISSUED",
        page_title="Refund Issued",
        header_title="Refund Issued",
        header_subtitle="A refund has been processed to your account",
        greeting_var="user_name",
        greeting_default="User",
        greeting_prefix="Dear",
        body_html="₹<strong style=\"color:#1A8491;\">{{ amount | default('N/A') }}</strong> refund has been issued to your account.",
        details_title="Refund Details",
        details=[("Amount", "amount")],
    ),
    dict(
        filename="PAYMENT_FAILED",
        page_title="Payment Failed",
        header_title="Payment Failed",
        header_subtitle="Your payment could not be processed",
        greeting_var="user_name",
        greeting_default="User",
        greeting_prefix="Dear",
        body_html="Your payment of ₹<strong style=\"color:#1A8491;\">{{ amount | default('N/A') }}</strong> failed. Please try again.",
        details_title="Payment Details",
        details=[("Amount", "amount")],
        instruction_emoji="💳",
        instruction_text="Please check your payment method and try again, or contact support if the issue persists.",
    ),
    dict(
        filename="PAYMENT_RECEIVED",
        page_title="Payment Successful",
        header_title="Payment Successful",
        header_subtitle="Your payment was processed successfully",
        greeting_var="user_name",
        greeting_default="User",
        greeting_prefix="Dear",
        body_html="Your payment of ₹<strong style=\"color:#1A8491;\">{{ amount | default('N/A') }}</strong> was successful.",
        details_title="Payment Details",
        details=[("Amount", "amount")],
        instruction_emoji="✅",
        instruction_text="Thank you for your payment. A receipt may be available in your account.",
    ),
    dict(
        filename="NEW_OFFER",
        page_title="New Offer",
        header_title="New Offer",
        header_subtitle="A new offer is available on Triphavenco",
        greeting_var="user_name",
        greeting_default="User",
        greeting_prefix="Dear",
        body_html="A new offer is available on Triphavenco. Check now and save money.",
        instruction_emoji="🎁",
        instruction_text="Open the <strong style=\"color:#1A8491;\">Triphavenco app</strong> to view and redeem this offer.",
    ),
]

if __name__ == "__main__":
    for t in TEMPLATES:
        render(**t)
