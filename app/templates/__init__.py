"""
Email templates module
Contains HTML email templates for various use cases
"""

from .template_loader import TemplateLoader
from .template_types import EmailTemplateType
from .push_template_loader import PushTemplateLoader
from .push_template_types import PushNotificationTemplateType

__all__ = [
    "TemplateLoader",
    "EmailTemplateType",
    "PushTemplateLoader",
    "PushNotificationTemplateType",
]

