# Heaven Connect Communication Server

A FastAPI microservice for handling email and push notification communications. This service integrates with Zoho Mail API for email sending and OneSignal for push notifications.

## Features

- 📧 **Email Service**: Send emails using Zoho Mail API with OAuth2 authentication
- 🎨 **Email Templates**: Pre-built HTML email templates with variable substitution
- ⏰ **Email Scheduling**: Schedule emails for one-time, daily, weekly, or monthly delivery
- 🔔 **Push Notifications**: Send push notifications using OneSignal API
- 🏗️ **Modular Architecture**: Clean, maintainable module-based structure
- 🔒 **Environment-based Configuration**: Secure credential management via `.env` file
- 📚 **Auto-generated API Documentation**: Swagger UI and ReDoc available

## Project Structure

```
heaven-connect-communication/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── email.py
│   │   └── push_notification.py
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── email_service.py
│   │   └── push_notification_service.py
│   └── routers/                # API route handlers
│       ├── __init__.py
│       ├── email.py
│       └── push_notification.py
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory based on `env.example`:

```bash
# On Windows (PowerShell)
Copy-Item env.example .env

# On Linux/Mac
cp env.example .env
```

**Note:** The application will start without a `.env` file, but email and push notification services will return errors until the required credentials are configured.

Then fill in your credentials:

#### Zoho Mail Configuration

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Create a new application
3. Generate OAuth2 credentials (Client ID, Client Secret)
4. Generate a refresh token
5. Get your Zoho account ID

#### OneSignal Configuration

1. Go to [OneSignal Dashboard](https://app.onesignal.com/)
2. Create a new app or select an existing one
3. Get your App ID and REST API Key from Settings > Keys & IDs

### 3. Run the Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Email Endpoints

#### Send Email (Template-based)
```http
POST /api/v1/email/send
Content-Type: application/json

{
  "to": ["user@example.com"],
  "template_type": "welcome",
  "template_context": {
    "user_name": "John Doe",
    "verification_link": "https://heavenconnect.com/verify?token=abc123"
  }
}
```

#### Send Email (Direct Content)
```http
POST /api/v1/email/send
Content-Type: application/json

{
  "to": ["user@example.com"],
  "subject": "Welcome to Heaven Connect",
  "body": "<h1>Welcome!</h1><p>Thank you for joining us.</p>",
  "cc": ["manager@example.com"],
  "is_html": true
}
```

#### Schedule Email
```http
POST /api/v1/email/schedule
Content-Type: application/json

{
  "email": {
    "to": ["user@example.com"],
    "template_type": "booking_reminder",
    "template_context": {
      "guest_name": "John Doe",
      "property_name": "Beach Villa",
      "check_in_date": "2024-12-20",
      "days_until_checkin": 5
    }
  },
  "schedule": {
    "schedule_type": "monthly",
    "monthly_day": 15,
    "monthly_time": "09:00"
  }
}
```

#### List Scheduled Emails
```http
GET /api/v1/email/schedule
```

#### Get Scheduled Email
```http
GET /api/v1/email/schedule/{schedule_id}
```

#### Cancel Scheduled Email
```http
DELETE /api/v1/email/schedule/{schedule_id}
```

#### Email Health Check
```http
GET /api/v1/email/health
```

### Push Notification Endpoints

#### Send Push Notification
```http
POST /api/v1/push/send
Content-Type: application/json

{
  "user_ids": ["player-id-1", "player-id-2"],
  "headings": {"en": "New Booking"},
  "contents": {"en": "You have a new booking request"},
  "data": {"booking_id": "123", "type": "booking"},
  "url": "https://heavenconnect.com/bookings/123"
}
```

#### Push Notification Health Check
```http
GET /api/v1/push/health
```

### General Endpoints

#### Root
```http
GET /
```

#### Health Check
```http
GET /health
```

## Environment Variables

See `.env.example` for all required environment variables:

- `ZOHO_CLIENT_ID`: Zoho OAuth2 Client ID
- `ZOHO_CLIENT_SECRET`: Zoho OAuth2 Client Secret
- `ZOHO_REFRESH_TOKEN`: Zoho OAuth2 Refresh Token
- `ZOHO_ACCOUNT_ID`: Zoho Account ID
- `ZOHO_FROM_EMAIL`: Default sender email address
- `ZOHO_FROM_NAME`: Default sender name
- `ONESIGNAL_APP_ID`: OneSignal Application ID
- `ONESIGNAL_REST_API_KEY`: OneSignal REST API Key

## Email Templates

The service includes pre-built email templates for common use cases:

- `welcome` - Welcome email for new users
- `user_registration` - User registration confirmation
- `email_verification` - Email verification
- `password_reset` - Password reset request
- `booking_confirmed` - Booking confirmation
- `booking_reminder` - Booking reminder
- `booking_cancelled` - Booking cancellation
- `payment_received` - Payment confirmation
- `review_request` - Review request
- `general_notification` - General notifications
- And more...

See `app/templates/template_types.py` for the complete list.

## Usage Examples

### Python Example

```python
import httpx

# Send email using template
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/email/send",
        json={
            "to": ["user@example.com"],
            "template_type": "welcome",
            "template_context": {
                "user_name": "John Doe",
                "verification_link": "https://heavenconnect.com/verify?token=abc123"
            }
        }
    )
    print(response.json())

# Send email with direct content
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/email/send",
        json={
            "to": ["user@example.com"],
            "subject": "Test Email",
            "body": "This is a test email",
            "is_html": False
        }
    )
    print(response.json())

# Schedule email (monthly on 15th at 9 AM)
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/email/schedule",
        json={
            "email": {
                "to": ["user@example.com"],
                "template_type": "booking_reminder",
                "template_context": {
                    "guest_name": "John Doe",
                    "property_name": "Beach Villa",
                    "check_in_date": "2024-12-20"
                }
            },
            "schedule": {
                "schedule_type": "monthly",
                "monthly_day": 15,
                "monthly_time": "09:00"
            }
        }
    )
    print(response.json())

# Send push notification
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/push/send",
        json={
            "user_ids": ["player-id-123"],
            "headings": {"en": "Hello"},
            "contents": {"en": "This is a test notification"}
        }
    )
    print(response.json())
```

### cURL Example

```bash
# Send email
curl -X POST "http://localhost:8000/api/v1/email/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["user@example.com"],
    "subject": "Test Email",
    "body": "This is a test email",
    "is_html": false
  }'

# Send push notification
curl -X POST "http://localhost:8000/api/v1/push/send" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": ["player-id-123"],
    "headings": {"en": "Hello"},
    "contents": {"en": "This is a test notification"}
  }'
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Structure

- **Models**: Pydantic models for request/response validation
- **Services**: Business logic for email and push notification operations
- **Routers**: FastAPI route handlers that expose the services via HTTP
- **Config**: Centralized configuration management using environment variables

## License

This project is part of the Heaven Connect platform.

