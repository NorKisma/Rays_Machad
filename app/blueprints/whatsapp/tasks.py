from ...extensions import celery, db
from ...utils.messaging import MessagingService
from ...models.message_log import MessageLog
from flask import current_app
import json

@celery.task(bind=True, max_retries=3, default_retry_delay=60, rate_limit='10/s')
def send_whatsapp_template_task(self, recipient_id, template_name, language_code="en_US", components=None, log_id=None):
    """
    Celery task to send a WhatsApp template message asynchronously.
    """
    messenger = MessagingService()
    try:
        success, response = messenger.send_whatsapp_template(recipient_id, template_name, language_code, components)
        
        if log_id:
            # Re-query the log within the task context
            log = MessageLog.query.get(log_id)
            if log:
                if success:
                    log.status = 'sent' 
                    if isinstance(response, dict) and response.get('messages'):
                        log.provider_message_id = response['messages'][0]['id']
                    log.error_message = None
                else:
                    log.status = 'failed'
                    log.error_message = f"Error: {response}"
                db.session.commit()

        return response

    except Exception as exc:
        current_app.logger.exception(f"Exception in send_whatsapp_template_task: {exc}")
        if log_id:
            try:
                log = MessageLog.query.get(log_id)
                if log:
                    log.status = 'failed'
                    log.error_message = str(exc)
                    db.session.commit()
            except:
                pass
                
        raise self.retry(exc=exc)

@celery.task(bind=True, max_retries=3, default_retry_delay=60, rate_limit='10/s')
def send_whatsapp_text_task(self, recipient_id, text_body, log_id=None):
    """
    Celery task to send a WhatsApp text message asynchronously.
    """
    messenger = MessagingService()
    try:
        success, response = messenger.send_whatsapp(recipient_id, text_body)
        
        if log_id:
            log = MessageLog.query.get(log_id)
            if log:
                if success:
                    log.status = 'sent'
                    if isinstance(response, dict) and response.get('messages'):
                        log.provider_message_id = response['messages'][0]['id']
                    log.error_message = None
                else:
                    log.status = 'failed'
                    log.error_message = f"Error: {response}"
                db.session.commit()

        return response

    except Exception as exc:
        current_app.logger.exception(f"Exception in send_whatsapp_text_task: {exc}")
        if log_id:
            try:
                log = MessageLog.query.get(log_id)
                if log:
                    log.status = 'failed'
                    log.error_message = str(exc)
                    db.session.commit()
            except:
                pass
        raise self.retry(exc=exc)
