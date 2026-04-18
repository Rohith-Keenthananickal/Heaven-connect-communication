"""
Gmail SMTP email service
Sends mail through Gmail (or Google Workspace) using SMTP and an app password.
"""

import asyncio
import logging
import mimetypes
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Any, Dict, List, Optional

from app.config import settings
from app.templates.template_loader import TemplateLoader
from app.templates.template_types import EmailTemplateType

logger = logging.getLogger(__name__)


def _domain_from_email(addr: str) -> str:
    if "@" in addr:
        return addr.rsplit("@", 1)[1]
    return "localhost"


def _send_via_gmail_smtp(
    *,
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    from_email: str,
    from_name: Optional[str],
    to: List[str],
    subject: str,
    body: str,
    is_html: bool,
    cc: Optional[List[str]],
    bcc: Optional[List[str]],
    reply_to: Optional[str],
    attachments: Optional[List[str]],
) -> str:
    """Blocking SMTP send (invoked via asyncio.to_thread). Returns Message-ID."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = (
        formataddr((from_name, from_email)) if from_name else from_email
    )
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if reply_to:
        msg["Reply-To"] = reply_to

    message_id = make_msgid(domain=_domain_from_email(from_email))
    msg["Message-ID"] = message_id

    if is_html:
        msg.set_content(
            "This message requires an HTML-capable email client.",
            subtype="plain",
            charset="utf-8",
        )
        msg.add_alternative(body, subtype="html", charset="utf-8")
    else:
        msg.set_content(body, subtype="plain", charset="utf-8")

    for path in attachments or []:
        if not path or not os.path.isfile(path):
            logger.warning("Attachment path missing or not a file: %s", path)
            continue
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            data = f.read()
        msg.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=os.path.basename(path),
        )

    envelope_to: List[str] = list(to)
    if cc:
        envelope_to.extend(cc)
    if bcc:
        envelope_to.extend(bcc)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg, from_addr=from_email, to_addrs=envelope_to)

    return message_id


class EmailService:
    """Service for sending emails via Gmail SMTP."""

    def __init__(self):
        self.smtp_host = settings.GMAIL_SMTP_HOST
        self.smtp_port = settings.GMAIL_SMTP_PORT
        self.username = settings.GMAIL_ADDRESS
        self.password = settings.GMAIL_APP_PASSWORD
        self.from_email = settings.effective_gmail_from_address()
        self.from_name = settings.GMAIL_FROM_NAME

    async def send_email(
        self,
        to: List[str],
        subject: Optional[str] = None,
        body: Optional[str] = None,
        template_type: Optional[EmailTemplateType] = None,
        template_context: Optional[Dict[str, Any]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        is_html: bool = True,
        reply_to: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> dict:
        """
        Send an email via Gmail SMTP.

        Args:
            to: List of recipient email addresses
            subject: Email subject (required if template_type not provided)
            body: Email body (required if template_type not provided)
            template_type: Email template type (optional)
            template_context: Context variables for template (required if template_type provided)
            cc: Optional list of CC email addresses
            bcc: Optional list of BCC email addresses
            is_html: Whether the body is HTML content
            reply_to: Optional reply-to email address
            attachments: Optional list of attachment file paths

        Returns:
            dict: Response containing message_id and status (same shape as before)
        """
        try:
            if not settings.validate_gmail_config():
                return {
                    "success": False,
                    "message_id": None,
                    "message": "Gmail configuration is incomplete",
                    "error": (
                        "Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your environment. "
                        "With 2-Step Verification on, use an App Password from your Google Account."
                    ),
                }

            if template_type:
                if not template_context:
                    return {
                        "success": False,
                        "message_id": None,
                        "message": "template_context is required when template_type is provided",
                        "error": "Missing template_context",
                    }

                try:
                    context_data = (
                        template_context.model_dump(exclude_none=True)
                        if hasattr(template_context, "model_dump")
                        else dict(template_context)
                    )
                    from datetime import datetime

                    if "current_year" not in context_data:
                        context_data["current_year"] = datetime.now().year

                    rendered_subject, rendered_body = TemplateLoader.render_template(
                        template_type=template_type,
                        context=context_data,
                    )
                    subject = subject or rendered_subject
                    body = rendered_body
                    is_html = True
                except Exception as e:
                    return {
                        "success": False,
                        "message_id": None,
                        "message": "Failed to render email template",
                        "error": str(e),
                    }
            else:
                if not subject or not body:
                    return {
                        "success": False,
                        "message_id": None,
                        "message": "subject and body are required when template_type is not provided",
                        "error": "Missing subject or body",
                    }

            message_id = await asyncio.to_thread(
                _send_via_gmail_smtp,
                smtp_host=self.smtp_host,
                smtp_port=self.smtp_port,
                username=self.username,
                password=self.password,
                from_email=self.from_email,
                from_name=self.from_name,
                to=to,
                subject=subject,
                body=body,
                is_html=is_html,
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
                attachments=attachments,
            )

            logger.info("Email sent successfully. Message-ID: %s", message_id)

            return {
                "success": True,
                "message_id": str(message_id) if message_id else None,
                "message": "Email sent successfully",
            }

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error sending email: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "message_id": None,
                "message": "Failed to send email",
                "error": error_msg,
            }
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message_id": None,
                "message": "Failed to send email",
                "error": error_msg,
            }
