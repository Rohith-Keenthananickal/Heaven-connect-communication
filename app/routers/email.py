"""
Email API router
Handles HTTP endpoints for email operations
"""

from fastapi import APIRouter, Body, HTTPException, status
from app.models.email import EmailRequest, EmailResponse, ScheduledEmailRequest, SEND_EMAIL_OPENAPI_EXAMPLES
from app.models.schedule import ScheduleRequest, ScheduleResponse
from app.services.email_service import EmailService
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/api/email", tags=["Email"])

# Initialize services
email_service = EmailService()
scheduler_service = SchedulerService()





@router.post("/send", response_model=EmailResponse, status_code=status.HTTP_200_OK)
async def send_email(
    email_request: EmailRequest = Body(
        ...,
        openapi_examples=SEND_EMAIL_OPENAPI_EXAMPLES,
        description="Send a Triphavenco templated email or raw HTML via Gmail SMTP.",
    ),
):
    """
    Send an email using Gmail SMTP.

    ## Modes

    1. **Template-based** — set `template_type` + `template_context` (recommended).
    2. **Direct content** — set `subject` + `body` (no template).

    Use the **Examples** dropdown in Swagger to pre-fill common requests.

    ## Template types

    | Category | template_type | Typical context |
    |----------|---------------|-----------------|
    | ATP | HOST_REGISTRATION_ATP | atp_name, host_name, location |
    | ATP | NEW_PROPERTY_SUBMITTED_ATP, PROPERTY_UPDATED_ATP | atp_name, host_name, property_name |
    | ATP | NEW_BOOKING_ATP | atp_name, property_name, guest_name, checkin_date, checkout_date |
    | ATP | GUEST_COMPLAINT_ATP, HOST_SUSPENDED_ATP | atp_name, guest_name, property_name / host_name |
    | ATP | ATP_REGISTRATION_SUBMITTED, ATP_ASSIGNED_AREA | atp_name, area |
    | ATP | ATP_APPROVED, ATP_REJECTED, ATP_ACCOUNT_ACTIVATED, ATP_ACCOUNT_SUSPENDED | atp_name |
    | Host | HOST_REGISTRATION_SUBMITTED, HOST_ACCOUNT_* | host_name |
    | Host | PROPERTY_APPROVED, PROPERTY_REJECTED | host_name, property_name |
    | Host | NEW_BOOKING_RECEIVED_HOST, HOST_BOOKING_CANCELLED | host_name, guest_name, property_name |
    | Host | GUEST_CHECK_IN_REMINDER_HOST, REVIEW_RECEIVED | host_name, guest_name, checkin_date |
    | Common | OTP, LOGIN, PASSWORD_RESET | user_name, otp / otp_code |
    | Common | PAYMENT_RECEIVED, PAYMENT_FAILED, REFUND_ISSUED | user_name, amount |
    | Support | SUPPORT_CREATED | user_name, issue, description, issue_code |
    | Legacy | WELCOME, EMAIL_VERIFICATION, BOOKING_* | varies |

    Subject defaults come from the template registry; override with `template_context.subject`.

    ## Request fields

    - **to** — recipient addresses (required)
    - **template_type** — enum value matching an HTML file under `app/templates/html/`
    - **template_context** — required when using a template
    - **subject**, **body** — required for direct (non-template) sends
    - **cc**, **bcc**, **reply_to**, **attachments** — optional
    - **is_html** — default `true`
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
        "provider": "gmail",
    }

