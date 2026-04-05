import requests
import json
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MessagingService:
    def __init__(self):
        from app.models.setting import SystemSetting
        # WhatsApp Config
        self.whatsapp_token = SystemSetting.get_setting('whatsapp_access_token')
        self.whatsapp_phone_number_id = SystemSetting.get_setting('whatsapp_phone_number_id')
        self.whatsapp_mode = SystemSetting.get_setting('whatsapp_mode', 'mock')
        
        # TextBee SMS Config
        self.textbee_api_key = current_app.config.get('TEXTBEE_API_KEY')
        self.textbee_device_id = current_app.config.get('TEXTBEE_DEVICE_ID')
        
        self.is_mock = (self.whatsapp_mode == 'mock')
        self.api_version = "v22.0"
        self.base_url = "https://graph.facebook.com"

    def _format_number(self, number):
        """Clean and format phone number for WhatsApp."""
        if not number: return None
        # Remove spaces, dashes, etc.
        clean = "".join(filter(str.isdigit, str(number)))
        # If it doesn't have a country code (starting with 252 for Somalia), prepend it if logical
        if len(clean) == 9 and not clean.startswith('252'):
            clean = "252" + clean
        return clean

    def _log_message(self, to, body, status, error=None, msg_type='general'):
        try:
            from app.models.message_log import MessageLog
            from app.extensions import db
            log = MessageLog(
                recipient=to,
                message_body=body,
                status=status,
                error_message=str(error) if error else None,
                message_type=msg_type
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logger.error(f"[ERROR LOGGING] {str(e)}")

    def send_whatsapp(self, to, message, msg_type='general'):
        """Send a simple text message via WhatsApp."""
        if self.is_mock:
            print(f"[MOCK WHATSAPP] To: {to} | Message: {message}")
            self._log_message(to, message, 'sent (mock)', msg_type=msg_type)
            return True, "Mock Success"

        formatted_to = self._format_number(to)
        if not formatted_to:
            return False, "Invalid phone number"

        if not self.whatsapp_token or not self.whatsapp_phone_number_id:
            return False, "WhatsApp not configured"

        url = f"{self.base_url}/{self.api_version}/{self.whatsapp_phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": formatted_to,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                self._log_message(formatted_to, message, 'sent', msg_type=msg_type)
                return True, response.json()
            else:
                error_text = response.text
                self._log_message(formatted_to, message, 'failed', error=error_text, msg_type=msg_type)
                return False, error_text
        except Exception as e:
            self._log_message(formatted_to, message, 'failed', error=str(e), msg_type=msg_type)
            return False, str(e)

    def send_whatsapp_template(self, to, template_name, language_code="en_US", components=None, msg_type='general'):
        """Send a template message via WhatsApp."""
        if self.is_mock:
            print(f"[MOCK WHATSAPP TEMPLATE] To: {to} | Template: {template_name}")
            self._log_message(to, f"Template: {template_name}", 'sent (mock)', msg_type=msg_type)
            return True, "Mock Success"

        formatted_to = self._format_number(to)
        if not formatted_to or not self.whatsapp_token or not self.whatsapp_phone_number_id:
            return False, "WhatsApp configuration or number invalid"

        url = f"{self.base_url}/{self.api_version}/{self.whatsapp_phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or []
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                self._log_message(formatted_to, f"Template: {template_name}", 'sent', msg_type=msg_type)
                return True, response.json()
            else:
                error_text = response.text
                self._log_message(formatted_to, f"Template: {template_name}", 'failed', error=error_text, msg_type=msg_type)
                return False, error_text
        except Exception as e:
            return False, str(e)

    def send_textbee_sms(self, to, message):
        """Send SMS via TextBee API."""
        if self.is_mock:
            print(f"[MOCK SMS] To: {to} | Message: {message}")
            return True, "Mock Success"

        if not self.textbee_api_key or not self.textbee_device_id:
             return False, "TextBee SMS Provider not configured"

        url = f"https://api.textbee.dev/api/v1/gateway/devices/{self.textbee_device_id}/send-sms"
        headers = {
            "x-api-key": self.textbee_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "recipients": [str(to)],
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                return True, "SMS Sent via TextBee"
            else:
                return False, f"TextBee Error: {response.text}"
        except Exception as e:
            return False, f"TextBee Exception: {str(e)}"

    def send_hybrid_message(self, to, message, msg_type='general'):
        """Hybrid Logic: Try WhatsApp first, Fallback to SMS."""
        # 1. Try WhatsApp
        success, response = self.send_whatsapp(to, message, msg_type)
        if success:
            return True, f"Sent via WhatsApp: {response}"
            
        # 2. Fallback to SMS if WhatsApp failed
        print(f"[HYBRID FALLBACK] WhatsApp failed... Trying SMS.")
        
        sms_success, sms_response = self.send_textbee_sms(to, message)
        if sms_success:
            self._log_message(to, message, 'sent (sms-fallback)', msg_type=msg_type)
            return True, f"Sent via SMS (Fallback): {sms_response}"
        else:
            # Clean up the error message for the user if it's too technical
            error_reason = f"WA: {response} | SMS: {sms_response}"
            self._log_message(to, message, 'failed', error=error_reason, msg_type=msg_type)
            return False, f"All channels failed. Please check provider status or credentials."

    def send_ai_report(self, parent_name, phone, student_info):
        """Combined method to send AI report using Hybrid logic."""
        if not phone:
            return False, "Missing phone number"
        return self.send_hybrid_message(phone, student_info, msg_type='monthly_report')
