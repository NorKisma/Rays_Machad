import requests
import uuid
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class IPayService:
    """
    Service for Hormuud Waafi (iPay) API Integration.
    Commonly used in Somali regions for EVC Plus, eDahab, and Waafi payments.
    """
    def __init__(self):
        # Configuration from app config
        self.api_key = current_app.config.get('IPAY_API_KEY')
        self.merchant_id = current_app.config.get('IPAY_MERCHANT_ID')
        self.api_user_id = current_app.config.get('IPAY_API_USER_ID')
        self.base_url = "https://api.waafipay.net/v1/gateway"

    def initiate_payment(self, phone, amount, description="Rays Machad Subscription"):
        """
        Triggers a USSD push (EVC Plus / Waafi) to the user's phone.
        """
        transaction_id = str(uuid.uuid4())
        
        payload = {
            "schemaVersion": "1.0",
            "requestId": transaction_id,
            "timestamp": "string",
            "channelName": "WEB",
            "serviceName": "API_PURCHASE",
            "serviceParams": {
                "merchantUid": self.merchant_id,
                "apiUserId": self.api_user_id,
                "apiKey": self.api_key,
                "paymentMethod": "MWALLET_ACCOUNT",
                "payerInfo": {
                    "accountNo": phone
                },
                "transactionInfo": {
                    "amount": str(amount),
                    "currency": "USD",
                    "description": description,
                    "referenceId": transaction_id
                }
            }
        }

        # If keys are missing, we run in MOCK mode
        if not self.api_key or not self.merchant_id or not self.api_user_id:
            logger.info(f"[MOCK PAYMENT] Initiating ${amount} for {phone}")
            return True, {
                "status": "PENDING",
                "transactionId": transaction_id,
                "message": "Payment request sent (MOCK)"
            }

        try:
            response = requests.post(self.base_url, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"API Error: {response.text}"
        except Exception as e:
            logger.error(f"IPay Request Failed: {str(e)}")
            return False, str(e)

    def check_status(self, transaction_id):
        """Checks the status of a previous transaction."""
        # Implementation for status check API
        pass
