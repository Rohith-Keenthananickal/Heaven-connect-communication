"""
Email scheduling models
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class ScheduleRequest(BaseModel):
    """Request model for scheduling emails"""
    
    schedule_type: Literal["once", "daily", "weekly", "monthly"] = Field(
        ...,
        description="Type of schedule: 'once' for one-time, 'daily' for daily, 'weekly' for weekly, 'monthly' for monthly"
    )
    
    # For 'once' schedule
    send_at: Optional[datetime] = Field(
        None,
        description="Specific date and time to send (required for 'once' schedule)"
    )
    
    # For 'daily' schedule
    daily_time: Optional[str] = Field(
        None,
        description="Time of day to send (HH:MM format, required for 'daily' schedule)"
    )
    
    # For 'weekly' schedule
    weekly_day: Optional[int] = Field(
        None,
        ge=0,
        le=6,
        description="Day of week (0=Monday, 6=Sunday, required for 'weekly' schedule)"
    )
    weekly_time: Optional[str] = Field(
        None,
        description="Time of day to send (HH:MM format, required for 'weekly' schedule)"
    )
    
    # For 'monthly' schedule
    monthly_day: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Day of month (1-31, required for 'monthly' schedule)"
    )
    monthly_time: Optional[str] = Field(
        None,
        description="Time of day to send (HH:MM format, required for 'monthly' schedule)"
    )
    
    # Optional: End date for recurring schedules
    end_date: Optional[datetime] = Field(
        None,
        description="End date for recurring schedules (optional)"
    )
    
    @model_validator(mode='after')
    def validate_schedule_requirements(self):
        """Validate that required fields are provided based on schedule type"""
        if self.schedule_type == "once":
            if not self.send_at:
                raise ValueError("send_at is required for 'once' schedule type")
        elif self.schedule_type == "daily":
            if not self.daily_time:
                raise ValueError("daily_time is required for 'daily' schedule type")
        elif self.schedule_type == "weekly":
            if self.weekly_day is None:
                raise ValueError("weekly_day is required for 'weekly' schedule type")
            if not self.weekly_time:
                raise ValueError("weekly_time is required for 'weekly' schedule type")
        elif self.schedule_type == "monthly":
            if self.monthly_day is None:
                raise ValueError("monthly_day is required for 'monthly' schedule type")
            if not self.monthly_time:
                raise ValueError("monthly_time is required for 'monthly' schedule type")
        
        return self
    
    @field_validator('daily_time', 'weekly_time', 'monthly_time')
    @classmethod
    def validate_time_format(cls, v):
        """Validate time format (HH:MM)"""
        if v:
            try:
                hour, minute = v.split(':')
                hour = int(hour)
                minute = int(minute)
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Time must be in HH:MM format with valid hours (0-23) and minutes (0-59)")
            except ValueError as e:
                if "invalid literal" in str(e) or "not enough values" in str(e):
                    raise ValueError("Time must be in HH:MM format")
                raise
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "schedule_type": "monthly",
                "monthly_day": 15,
                "monthly_time": "09:00",
                "end_date": "2024-12-31T23:59:59"
            }
        }


class ScheduleResponse(BaseModel):
    """Response model for scheduled email operations"""
    
    success: bool = Field(..., description="Whether the email was scheduled successfully")
    schedule_id: Optional[str] = Field(None, description="Unique schedule ID")
    scheduled_for: Optional[datetime] = Field(None, description="When the email will be sent")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "schedule_id": "schedule-123",
                "scheduled_for": "2024-12-15T09:00:00",
                "message": "Email scheduled successfully"
            }
        }

