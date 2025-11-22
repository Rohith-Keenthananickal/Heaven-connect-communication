"""
Email API router
Handles HTTP endpoints for email operations
"""

from fastapi import APIRouter, HTTPException, status
from app.models.email import EmailRequest, EmailResponse, ScheduledEmailRequest
from app.models.schedule import ScheduleRequest, ScheduleResponse
from app.services.email_service import EmailService
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/api/email", tags=["Email"])

# Initialize services
email_service = EmailService()
scheduler_service = SchedulerService()


@router.post("/send", response_model=EmailResponse, status_code=status.HTTP_200_OK)
async def send_email(email_request: EmailRequest):
    """
    Send an email using Zoho Mail API
    
    Supports two modes:
    1. **Template-based**: Provide `template_type` and `template_context`
    2. **Direct content**: Provide `subject` and `body` directly
    
    - **to**: List of recipient email addresses
    - **template_type**: Email template type (optional, use template or direct content)
    - **template_context**: Context variables for template (required if template_type provided)
    - **subject**: Email subject (required if template_type not provided)
    - **body**: Email body (required if template_type not provided)
    - **cc**: Optional list of CC email addresses
    - **bcc**: Optional list of BCC email addresses
    - **is_html**: Whether the body is HTML content (default: True)
    - **reply_to**: Optional reply-to email address
    - **attachments**: Optional list of attachment file paths
    """
    try:
        result = await email_service.send_email(
            to=email_request.to,
            subject=email_request.subject,
            body=email_request.body,
            template_type=email_request.template_type,
            template_context=email_request.template_context,
            cc=email_request.cc,
            bcc=email_request.bcc,
            is_html=email_request.is_html,
            reply_to=email_request.reply_to,
            attachments=email_request.attachments,
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send email"),
            )
        
        return EmailResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.post("/schedule", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
async def schedule_email(request: ScheduledEmailRequest):
    """
    Schedule an email to be sent at a specific time or recurring schedule
    
    - **email**: Email request (same structure as /send endpoint)
    - **schedule**: Schedule configuration
      - **schedule_type**: 'once', 'daily', 'weekly', or 'monthly'
      - **send_at**: Required for 'once' - specific datetime
      - **daily_time**: Required for 'daily' - time in HH:MM format
      - **weekly_day**: Required for 'weekly' - day of week (0=Monday, 6=Sunday)
      - **weekly_time**: Required for 'weekly' - time in HH:MM format
      - **monthly_day**: Required for 'monthly' - day of month (1-31)
      - **monthly_time**: Required for 'monthly' - time in HH:MM format
      - **end_date**: Optional end date for recurring schedules
    """
    try:
        # Prepare email data
        email_data = {
            "to": request.email.to,
            "subject": request.email.subject,
            "body": request.email.body,
            "template_type": request.email.template_type,
            "template_context": request.email.template_context,
            "cc": request.email.cc,
            "bcc": request.email.bcc,
            "is_html": request.email.is_html,
            "reply_to": request.email.reply_to,
            "attachments": request.email.attachments,
        }
        
        result = await scheduler_service.schedule_email(
            email_data=email_data,
            schedule=request.schedule
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to schedule email"),
            )
        
        return ScheduleResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.delete("/schedule/{schedule_id}", status_code=status.HTTP_200_OK)
async def cancel_scheduled_email(schedule_id: str):
    """
    Cancel a scheduled email
    
    - **schedule_id**: The ID of the scheduled email to cancel
    """
    result = scheduler_service.cancel_schedule(schedule_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message", "Schedule not found"),
        )
    
    return result


@router.get("/schedule/{schedule_id}", status_code=status.HTTP_200_OK)
async def get_scheduled_email(schedule_id: str):
    """
    Get information about a scheduled email
    
    - **schedule_id**: The ID of the scheduled email
    """
    schedule = scheduler_service.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    
    return {
        "schedule_id": schedule["schedule_id"],
        "schedule_type": schedule["schedule_type"],
        "scheduled_for": schedule["scheduled_for"],
    }


@router.get("/schedule", status_code=status.HTTP_200_OK)
async def list_scheduled_emails():
    """
    List all scheduled emails
    """
    schedules = scheduler_service.list_schedules()
    return {"schedules": schedules, "count": len(schedules)}


@router.get("/health", status_code=status.HTTP_200_OK)
async def email_health_check():
    """
    Health check endpoint for email service
    """
    return {
        "status": "healthy",
        "service": "email",
        "provider": "zoho",
    }

