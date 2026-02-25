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
    
    # Zoho Email Configuration
    ZOHO_CLIENT_ID: str = os.getenv("ZOHO_CLIENT_ID", "")
    ZOHO_CLIENT_SECRET: str = os.getenv("ZOHO_CLIENT_SECRET", "")
    ZOHO_REFRESH_TOKEN: str = os.getenv("ZOHO_REFRESH_TOKEN", "")
    ZOHO_ACCOUNT_ID: str = os.getenv("ZOHO_ACCOUNT_ID", "")
    ZOHO_FROM_EMAIL: str = os.getenv("ZOHO_FROM_EMAIL", "")
    ZOHO_FROM_NAME: Optional[str] = os.getenv("ZOHO_FROM_NAME", "Heaven Connect")
    ZOHO_API_DOMAIN: str = os.getenv("ZOHO_API_DOMAIN", "https://mail.zoho.in")
    
    # Auth0 Configuration (for Zoho authentication)
    AUTH0_DOMAIN: Optional[str] = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID: Optional[str] = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET: Optional[str] = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_AUDIENCE: Optional[str] = os.getenv("AUTH0_AUDIENCE")
    
    # OneSignal Configuration
    ONESIGNAL_APP_ID: str = (os.getenv("ONESIGNAL_APP_ID") or "").strip()
    ONESIGNAL_REST_API_KEY: str = (os.getenv("ONESIGNAL_REST_API_KEY") or "").strip()
    ONESIGNAL_API_URL: str = (os.getenv("ONESIGNAL_API_URL") or "https://onesignal.com/api/v1").strip()

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
settings = Settings()
