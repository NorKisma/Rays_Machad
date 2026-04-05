# WhatsApp Integration Guide (Production Focused)

This guide details the architecture and implementation of the WhatsApp integration for Madrasah Management. It follows best practices for reliability, rate limiting, and security.

## Architecture Overview

**Core Components:**
1.  **Flask Application**: Handles HTTP requests (API to trigger sending, API to receive webhooks).
2.  **Celery Worker**: Processes message sending asynchronously in the background. avoiding API latency and potential blocking of the main thread.
3.  **Redis**: Broker for Celery message queue and backend for rate limiting.
4.  **PostgreSQL**: Stores message logs (`MessageLog` model) for audit and status tracking.

**Flow:**
1.  **Sending**: `POST /whatsapp/send/template` -> Validates Input -> **Queues to Celery** -> Returns Task ID.
    *   *Celery Worker* picks up task -> Checks Rate Limit (10/s) -> Calls WhatsApp API -> Updates DB (Sent/Failed).
2.  **Receiving**: Meta sends webhook to `POST /whatsapp/webhook` -> Flask verifies -> Updates DB (Delivered/Read) or Logs Incoming Message.

## Configuration (.env)

Ensure these variables are set in `.env`:
```env
WHATSAPP_API_TOKEN=your_permanent_access_token_or_system_user_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=random_secure_string_for_webhook_verification
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Production Setup

### 1. Requirements
Ensure Redis is installed and running:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 2. Running the Worker (Background Queue)
For production, use Supervisor to keep the Celery worker running.

**Create Supervisor Config:** `/etc/supervisor/conf.d/madrasah_celery.conf`
```ini
[program:madrasah_celery]
directory=/var/www/RaysTech/madrasah_mgmt
command=/var/www/RaysTech/madrasah_mgmt/venv/bin/celery -A app.celery worker --loglevel=info
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/celery_err.log
stdout_logfile=/var/log/celery_out.log
```
Run `sudo supervisorctl reread && sudo supervisorctl update`.

### 3. HTTPS & Webhooks (Crucial)
Meta REQUIRES `https://` for webhooks.
-   **Domain**: `https://your-madrasah-domain.com`
-   **Webhook URL**: `https://your-madrasah-domain.com/whatsapp/webhook`
-   **Verify Token**: Must match `WHATSAPP_VERIFY_TOKEN` in `.env`.

In Meta App Dashboard > WhatsApp > Configuration:
1.  Click **Edit** under Callback URL.
2.  Enter the URL and Verify Token.
3.  Verify and Save.
4.  Click **Manage** under Webhook fields and subscribe to `messages`.

## Template Messages (Important)

Reference: [Meta Template Docs](https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates)

**Why Templates?**
You **cannot** send free-form text to a user who hasn't messaged you in the last 24 hours. You MUST use a pre-approved Template.

**How to create:**
1.  Go to [WhatsApp Manager](https://business.facebook.com/wa/manage/message-templates/).
2.  Create Template (e.g., `attendance_alert`).
3.  Category: Utility/Marketing.
4.  Body: `Dear {{1}}, your student {{2}} is absent today.`

**Sending via Code:**
Use the endpoint sending the `components` array strictly matching the variables.

**Payload Example:**
```json
POST /whatsapp/send/template
{
    "to": "25261xxxxxxx",
    "template": "attendance_alert",
    "language": "en_US",
    "components": [
        {
            "type": "body",
            "parameters": [
                { "type": "text", "text": "Ali Abdi" },     // {{1}} Parent Name
                { "type": "text", "text": "Mohamed Ali" }   // {{2}} Student Name
            ]
        }
    ]
}
```

## Rate Limiting & Safety

To prevent Meta from banning your number:
1.  **Internal Limiting**: The API endpoints (`/send/*`) are limited to **60 requests/minute** per IP using `Flask-Limiter`.
2.  **Outbound Limiting**: The Celery task is configured with `rate_limit='10/s'`. Even if you queue 1000 messages at once, the worker will only process 10 per second max.
3.  **Error Handling**: If Meta returns 5xx errors, Celery will auto-retry. If 4xx (Bad Request), it logs the error and stops to prevent spamming invalid requests.

## Logs
-   **Database**: Check `message_logs` table for status (`queued`, `sent`, `delivered`, `read`, `failed`).
-   **Files**: Check `app.log` (if configured) or Supervisor logs for worker errors.
