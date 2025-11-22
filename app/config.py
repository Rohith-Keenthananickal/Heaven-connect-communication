"""
Configuration management for the application
Loads environment variables and provides configuration settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Heaven Connect Communication Server"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Zoho Email Configuration
    # Using empty strings as defaults to allow app startup without .env file
    # These will be validated when services are actually used
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    ZOHO_REFRESH_TOKEN: str = ""
    ZOHO_ACCOUNT_ID: str = ""
    ZOHO_FROM_EMAIL: str = ""
    ZOHO_FROM_NAME: Optional[str] = "Heaven Connect"
    ZOHO_API_DOMAIN: str = "https://mail.zoho.in"
    
    # Auth0 Configuration (for Zoho authentication)
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_CLIENT_ID: Optional[str] = None
    AUTH0_CLIENT_SECRET: Optional[str] = None
    AUTH0_AUDIENCE: Optional[str] = None
    
    # OneSignal Configuration
    # Using empty strings as defaults to allow app startup without .env file
    # These will be validated when services are actually used
    ONESIGNAL_APP_ID: str = ""
    ONESIGNAL_REST_API_KEY: str = ""
    ONESIGNAL_API_URL: str = "https://onesignal.com/api/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def validate_zoho_config(self) -> bool:
        """Validate that all required Zoho configuration is present"""
        required_fields = [
            self.ZOHO_CLIENT_ID,
            self.ZOHO_CLIENT_SECRET,
            self.ZOHO_REFRESH_TOKEN,
            self.ZOHO_ACCOUNT_ID,
            self.ZOHO_FROM_EMAIL,
        ]
        return all(field for field in required_fields)
    
    def validate_onesignal_config(self) -> bool:
        """Validate that all required OneSignal configuration is present"""
        return bool(self.ONESIGNAL_APP_ID and self.ONESIGNAL_REST_API_KEY)


# Global settings instance
# Will load from .env file if it exists, otherwise use defaults
settings = Settings()

