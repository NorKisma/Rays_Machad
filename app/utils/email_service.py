from flask_mail import Message
from app.extensions import mail
from flask import render_template, current_app
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_activation_email(recipient_email, password, school_name):
        """
        Sends an activation email to the new school admin.
        """
        try:
            subject = f"Welcome to Rays Madrasah - Activation Successful for {school_name}"
            msg = Message(subject=subject, recipients=[recipient_email])
            
            # Message body in Somali and English
            msg.body = f"""
Asc {school_name} Admin,
            
Hambalyo! Madrasadaada si guul leh  ayaa loo shiday (Activated) nidaamka Rays Madrasah.

Halkan waa macluumaadkaaga gelitaanka (Login Details):
- Email: {recipient_email}
- Password: {password}

Waxaad ka geli kartaa halkan: {current_app.config.get('BASE_URL', 'https://raystechcenter.online')}

Mahadsanid,
Kooxda Rays Tech
--------------------------------------------------
Congratulations! Your madrasah has been successfully activated on the Rays Madrasah system.

Here are your login details:
- Email: {recipient_email}
- Password: {password}

You can login here: {current_app.config.get('BASE_URL', 'https://raystechcenter.online')}

Thank you,
Rays Tech Team
            """
            
            mail.send(msg)
            logger.info(f"✅ Activation email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"❌ Error sending activation email to {recipient_email}: {str(e)}")
            return False

