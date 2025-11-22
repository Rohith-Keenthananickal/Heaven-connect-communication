"""
Player (Device) models for OneSignal registration
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Text
from sqlalchemy.dialects.mysql import CHAR
from pydantic import BaseModel, Field

from app.database import Base


class DeviceType(str, Enum):
    """Device type enum"""
    ANDROID = "android"
    IOS = "ios"
    IPAD = "ipad"
    MAC = "mac"
    TAB = "tab"
    WEB = "web"


class DeviceStatus(str, Enum):
    """Device status enum"""
    ACTIVE = "active"
    BLOCKED = "blocked"
    LOGOUT = "logout"


class Player(Base):
    """Player (Device) SQLAlchemy model"""
    __tablename__ = "players"

    player_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), nullable=False, index=True)
    device_type = Column(SQLEnum(DeviceType), nullable=False)
    push_token = Column(Text, nullable=False)
    device_model = Column(Text, nullable=True)
    os_version = Column(Text, nullable=True)
    app_version = Column(Text, nullable=True)
    last_login_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.ACTIVE)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas

class PlayerBase(BaseModel):
    """Base Player schema"""
    user_id: str = Field(..., description="User ID this device belongs to")
    device_type: DeviceType = Field(..., description="Device category")
    push_token: str = Field(..., description="FCM / APNs / OneSignal token")
    device_model: Optional[str] = Field(None, description="Device model (e.g. iPhone 14)")
    os_version: Optional[str] = Field(None, description="OS version")
    app_version: Optional[str] = Field(None, description="App version")


class PlayerCreate(PlayerBase):
    """Schema for registering a player"""
    pass


class PlayerUpdate(BaseModel):
    """Schema for updating a player"""
    push_token: Optional[str] = Field(None, description="Updated push token")
    device_model: Optional[str] = Field(None, description="Updated device model")
    os_version: Optional[str] = Field(None, description="Updated OS version")
    app_version: Optional[str] = Field(None, description="Updated app version")
    status: Optional[DeviceStatus] = Field(None, description="Updated status")


class PlayerResponse(PlayerBase):
    """Schema for player response"""
    player_id: str
    last_login_at: datetime
    status: DeviceStatus
    updated_at: datetime

    class Config:
        from_attributes = True
