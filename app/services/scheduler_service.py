"""
Email Scheduling Service
Handles scheduling emails using APScheduler
"""

import logging
import uuid
from datetime import datetime, time, timedelta
from typing import Dict, Any, Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.models.schedule import ScheduleRequest
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

# Global scheduler instance (will be started in lifespan)
scheduler = AsyncIOScheduler()

# Store scheduled job metadata
scheduled_jobs: Dict[str, Dict[str, Any]] = {}


class SchedulerService:
    """Service for scheduling email sending"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    async def schedule_email(
        self,
        email_data: Dict[str, Any],
        schedule: ScheduleRequest
    ) -> dict:
        """
        Schedule an email to be sent
        
        Args:
            email_data: Email data (to, subject, body, etc.)
            schedule: Schedule configuration
            
        Returns:
            dict: Response containing schedule_id and scheduled_for
        """
        try:
            schedule_id = str(uuid.uuid4())
            scheduled_for = None
            
            if schedule.schedule_type == "once":
                # One-time schedule
                if not schedule.send_at:
                    return {
                        "success": False,
                        "schedule_id": None,
                        "scheduled_for": None,
                        "message": "send_at is required for 'once' schedule",
                        "error": "Missing required field: send_at"
                    }
                
                scheduled_for = schedule.send_at
                trigger = DateTrigger(run_date=schedule.send_at)
                
                job = scheduler.add_job(
                    self._send_scheduled_email,
                    trigger=trigger,
                    id=schedule_id,
                    args=[email_data],
                    replace_existing=True
                )
                
            elif schedule.schedule_type == "daily":
                # Daily schedule
                hour, minute = map(int, schedule.daily_time.split(':'))
                trigger = CronTrigger(hour=hour, minute=minute)
                
                # Calculate next run time
                now = datetime.now()
                next_run = datetime.combine(now.date(), time(hour, minute))
                if next_run <= now:
                    next_run += timedelta(days=1)
                scheduled_for = next_run
                
                job = scheduler.add_job(
                    self._send_scheduled_email,
                    trigger=trigger,
                    id=schedule_id,
                    args=[email_data],
                    replace_existing=True,
                    end_date=schedule.end_date
                )
                
            elif schedule.schedule_type == "weekly":
                # Weekly schedule (0=Monday, 6=Sunday)
                hour, minute = map(int, schedule.weekly_time.split(':'))
                trigger = CronTrigger(day_of_week=schedule.weekly_day, hour=hour, minute=minute)
                
                # Calculate next run time
                now = datetime.now()
                days_ahead = (schedule.weekly_day - now.weekday()) % 7
                if days_ahead == 0 and datetime.combine(now.date(), time(hour, minute)) <= now:
                    days_ahead = 7
                next_run = datetime.combine(now.date(), time(hour, minute)) + timedelta(days=days_ahead)
                scheduled_for = next_run
                
                job = scheduler.add_job(
                    self._send_scheduled_email,
                    trigger=trigger,
                    id=schedule_id,
                    args=[email_data],
                    replace_existing=True,
                    end_date=schedule.end_date
                )
                
            elif schedule.schedule_type == "monthly":
                # Monthly schedule
                hour, minute = map(int, schedule.monthly_time.split(':'))
                trigger = CronTrigger(day=schedule.monthly_day, hour=hour, minute=minute)
                
                # Calculate next run time
                now = datetime.now()
                # Start with current month
                try:
                    next_run = now.replace(day=schedule.monthly_day, hour=hour, minute=minute, second=0, microsecond=0)
                except ValueError:
                    # If day doesn't exist in current month (e.g., Feb 30), use last day of month
                    from calendar import monthrange
                    last_day = monthrange(now.year, now.month)[1]
                    next_run = now.replace(day=min(schedule.monthly_day, last_day), hour=hour, minute=minute, second=0, microsecond=0)
                
                # If the time has passed this month, move to next month
                if next_run <= now:
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
                    
                    # Handle day overflow in next month
                    try:
                        next_run = next_run.replace(day=schedule.monthly_day)
                    except ValueError:
                        from calendar import monthrange
                        last_day = monthrange(next_run.year, next_run.month)[1]
                        next_run = next_run.replace(day=min(schedule.monthly_day, last_day))
                
                scheduled_for = next_run
                
                job = scheduler.add_job(
                    self._send_scheduled_email,
                    trigger=trigger,
                    id=schedule_id,
                    args=[email_data],
                    replace_existing=True,
                    end_date=schedule.end_date
                )
            
            # Store job metadata
            scheduled_jobs[schedule_id] = {
                "schedule_id": schedule_id,
                "schedule_type": schedule.schedule_type,
                "scheduled_for": scheduled_for,
                "email_data": email_data,
                "job": job
            }
            
            logger.info(f"Email scheduled successfully. Schedule ID: {schedule_id}, Scheduled for: {scheduled_for}")
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "scheduled_for": scheduled_for,
                "message": f"Email scheduled successfully for {scheduled_for}",
            }
            
        except Exception as e:
            error_msg = f"Error scheduling email: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "schedule_id": None,
                "scheduled_for": None,
                "message": "Failed to schedule email",
                "error": error_msg,
            }
    
    async def _send_scheduled_email(self, email_data: Dict[str, Any]):
        """Internal method to send a scheduled email"""
        try:
            result = await self.email_service.send_email(**email_data)
            logger.info(f"Scheduled email sent. Result: {result}")
        except Exception as e:
            logger.error(f"Error sending scheduled email: {str(e)}")
    
    def cancel_schedule(self, schedule_id: str) -> dict:
        """
        Cancel a scheduled email
        
        Args:
            schedule_id: The schedule ID to cancel
            
        Returns:
            dict: Response indicating success or failure
        """
        try:
            if schedule_id not in scheduled_jobs:
                return {
                    "success": False,
                    "message": f"Schedule ID {schedule_id} not found",
                }
            
            scheduler.remove_job(schedule_id)
            del scheduled_jobs[schedule_id]
            
            logger.info(f"Schedule {schedule_id} cancelled successfully")
            
            return {
                "success": True,
                "message": f"Schedule {schedule_id} cancelled successfully",
            }
            
        except Exception as e:
            error_msg = f"Error cancelling schedule: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": "Failed to cancel schedule",
                "error": error_msg,
            }
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule information by ID"""
        return scheduled_jobs.get(schedule_id)
    
    def list_schedules(self) -> List[Dict[str, Any]]:
        """List all scheduled emails"""
        return [
            {
                "schedule_id": job["schedule_id"],
                "schedule_type": job["schedule_type"],
                "scheduled_for": job["scheduled_for"],
            }
            for job in scheduled_jobs.values()
        ]

