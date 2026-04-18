"""
Configuration management for the application
Loads environment variables and provides configuration settings
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Heaven Connect Communication Server")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Gmail SMTP (use an App Password when 2-Step Verification is enabled)
    GMAIL_ADDRESS: str = os.getenv("GMAIL_ADDRESS", "")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")
    GMAIL_FROM_NAME: Optional[str] = os.getenv("GMAIL_FROM_NAME", "Heaven Connect")
    # Optional "Send mail as" address; must be allowed in Google account settings
    GMAIL_FROM_EMAIL: str = os.getenv("GMAIL_FROM_EMAIL", "")
    GMAIL_SMTP_HOST: str = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
    GMAIL_SMTP_PORT: int = int(os.getenv("GMAIL_SMTP_PORT", "587"))
    
    # Auth0 Configuration (optional)
    AUTH0_DOMAIN: Optional[str] = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID: Optional[str] = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET: Optional[str] = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_AUDIENCE: Optional[str] = os.getenv("AUTH0_AUDIENCE")
    
    # OneSignal Configuration
    ONESIGNAL_APP_ID: str = (os.getenv("ONESIGNAL_APP_ID") or "").strip()
    ONESIGNAL_REST_API_KEY: str = (os.getenv("ONESIGNAL_REST_API_KEY") or "").strip()
    ONESIGNAL_API_URL: str = (os.getenv("ONESIGNAL_API_URL") or "https://onesignal.com/api").strip()

    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "heaven_connect_communication")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from settings"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def effective_gmail_from_address(self) -> str:
        """From header address (alias if configured, otherwise the SMTP account)."""
        return (self.GMAIL_FROM_EMAIL or "").strip() or self.GMAIL_ADDRESS

    def validate_gmail_config(self) -> bool:
        """Validate that required Gmail SMTP configuration is present"""
        return bool(self.GMAIL_ADDRESS and self.GMAIL_APP_PASSWORD)
    
    def validate_onesignal_config(self) -> bool:
        """Validate that all required OneSignal configuration is present"""
        return bool(self.ONESIGNAL_APP_ID and self.ONESIGNAL_REST_API_KEY)


# Global settings instance
settings = Settings()
