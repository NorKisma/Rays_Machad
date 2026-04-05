# Webhook Setup Guide

This guide explains how to set up Webhooks for TextBee and WhatsApp to receive incoming messages and delivery reports.

## 1. What is a Webhook?
A Webhook allows TextBee (or WhatsApp) to "push" data to your server whenever an event happens—like receiving a new SMS. Without a webhook, your application won't know when someone replies.

## 2. TextBee Webhook Setup

### Step A: Identify Your Webhook URL
Your application is hosted at a specific domain. The webhook URL follows this format:

```
https://<your-domain>/madrasah/webhooks/textbee/sms
```

For example, if your site is `raystechcenter.online`, the URL is:
`https://raystechcenter.online/madrasah/webhooks/textbee/sms`

*(Note: Ensure your server is publicly accessible. If testing locally, use ngrok.)*

### Step B: Configure TextBee
1.  Log in to your [TextBee Dashboard](https://textbee.dev/dashboard).
2.  Go to **Webhooks** or **Device Settings**.
3.  Add a new Webhook for **Incoming SMS**.
4.  Paste your Webhook URL (from Step A).
5.  Save changes.

### Step C: Test It
Send an SMS to your TextBee-connected phone number.
1.  TextBee app receives the SMS.
2.  TextBee sends a POST request to your server.
3.  Your server logs the message to the database (check `Message Logs` in admin panel).

## 3. WhatsApp Webhook (Optional)

If you are using the official WhatsApp Business API, you can also set up a webhook.

*   **Webhook URL**: `https://<your-domain>/madrasah/webhooks/whatsapp`
*   **Verify Token**: Configure `WHATSAPP_VERIFY_TOKEN` in your `.env`.

## 4. Troubleshooting

*   **404 Not Found**: Check if the URL is correct (including `/madrasah` prefix).
*   **400 Bad Request**: The payload format might be different. Check logs: `supo journalctl -u madrasah -n 50`.
*   **CSRF Error**: Webhooks are exempted from CSRF protection, but ensure your server allows POST requests from external IPs.
