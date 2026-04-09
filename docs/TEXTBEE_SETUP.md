# TextBee SMS & WhatsApp Hybrid Setup Guide

This guide explains how to set up TextBee as your SMS provider and configure the hybrid messaging system (WhatsApp First -> SMS Fallback).

## 1. What is TextBee?
TextBee allows you to use your own Android phone as an SMS Gateway. This is a cost-effective way to send SMS messages using your existing mobile plan.

## 2. Step-by-Step Setup

### Step A: Download the App
1.  Download the **TextBee Gateway** app from the Google Play Store or their website (textbee.dev) on your Android phone.
2.  Sign in with your Google account.

### Step B: Get Credentials
1.  In the app, you will see your **Device ID**. Copy this.
2.  Go to the [TextBee Dashboard](https://textbee.dev/dashboard).
3.  Go to **API Keys** and generate a new key. Copy this **API Key**.

### Step C: Configure Your App
1.  Open the `.env` file on your server (at `/var/www/RaysTech/rays_machad_mgmt/.env`).
2.  Find the section `# TextBee SMS Configuration`.
3.  Update the values with your credentials:

```bash
# TextBee SMS Configuration
TEXTBEE_API_KEY=your_generated_api_key_here
TEXTBEE_DEVICE_ID=your_device_id_here
```

4.  Save the file and restart the service:
    ```bash
    sudo systemctl restart rays_machad
    ```

## 3. How the Hybrid System Works

The messaging system uses a "Smart Fallback" logic:

1.  **Try WhatsApp First**: The system attempts to send a WhatsApp message via the Meta Graph API.
2.  **Check Success**: If the message is sent successfully, it stops.
3.  **Fallback to SMS**: If WhatsApp fails (e.g., recipient not on WhatsApp, API error, or Mock mode), the system automatically switches to sending an SMS via TextBee.

### Code Logic (`app/utils/messaging.py`)

```python
    def send_hybrid_message(self, to, message, msg_type='general'):
        # 1. Try WhatsApp
        success, response = self.send_whatsapp(to, message, msg_type)
        if success:
            return True, f"Sent via WhatsApp: {response}"
            
        # 2. Fallback to SMS
        print(f"[HYBRID FALLBACK] WhatsApp failed... Trying SMS.")
        return self.send_sms(to, message)
```

## 4. Testing

To test the integration, you can use the `test_textbee.py` script (create one if needed) or trigger a monthly report for a student.

### Example Test Script
```python
from app.utils.messaging import MessagingService

ms = MessagingService()
# Test SMS directly
ms.send_textbee_sms("+1234567890", "Test SMS from Rays Machad App")

# Test Hybrid (will try WhatsApp first)
ms.send_hybrid_message("+1234567890", "Test Hybrid Message")
```

## 5. Troubleshooting

*   **"TextBee Error"**: Check if your Android phone is online and has the TextBee app running.
*   **"Provider not configured"**: Ensure you updated `.env` and restarted the service.
*   **Messages not delivering**: Verify you have SMS credit/balance on your SIM card.
