from flask import request, jsonify, current_app, abort
from app.extensions import limiter, db
from app.blueprints.whatsapp import whatsapp_bp
from app.blueprints.whatsapp.tasks import send_whatsapp_template_task, send_whatsapp_text_task
from app.models.message_log import MessageLog
from datetime import datetime

@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Webhook verification endpoint for Meta.
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    verify_token = current_app.config.get('WHATSAPP_VERIFY_TOKEN')

    if mode and token:
        if mode == 'subscribe' and token == verify_token:
            current_app.logger.info("WhatsApp Webhook Verified")
            return challenge, 200
        else:
            current_app.logger.warning(f"Webhook verification failed. Token: {token}")
            return 'Forbidden', 403
    return 'Bad Request', 400

@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook_handler():
    """
    Handle incoming webhook events (messages, statuses).
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "no data"}), 200

    try:
        # Check if it's a WhatsApp status update
        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    # Handle Status Updates (Sent, Delivered, Read, Failed)
                    if 'statuses' in value:
                        for status in value['statuses']:
                            msg_id = status.get('id')
                            status_str = status.get('status')
                            timestamp = status.get('timestamp')
                            
                            # Update MessageLog
                            log = MessageLog.query.filter_by(provider_message_id=msg_id).first()
                            if log:
                                log.status = status_str
                                # If failed, save error/reason
                                if status_str == 'failed':
                                    errors = status.get('errors', [])
                                    if errors:
                                        log.error_message = f"{errors[0].get('title')} - {errors[0].get('message')}"
                                db.session.commit()
                                current_app.logger.info(f"Message Status Updated: {msg_id} -> {status_str}")

                    # Handle Incoming Messages
                    if 'messages' in value:
                        for msg in value['messages']:
                            sender = msg.get('from')
                            msg_type = msg.get('type')
                            msg_body = ""
                            
                            if msg_type == 'text':
                                msg_body = msg.get('text', {}).get('body')
                            
                            current_app.logger.info(f"Received Message from {sender}: {msg_body}")
                            
                            # Here you could trigger an auto-reply or save to inbox
                            # For now, just logging is enough as per requirements.

        return jsonify({"status": "success"}), 200

    except Exception as e:
        current_app.logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error"}), 500

@whatsapp_bp.route('/send/template', methods=['POST'])
@limiter.limit("60 per minute") # Rate limit internal API calls
def send_template():
    """
    Endpoint to trigger sending a WhatsApp template message.
    Payload:
    {
        "to": "1234567890",
        "template": "hello_world",
        "language": "en_US",
        "components": [...]
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    recipient_id = data.get('to')
    template_name = data.get('template')
    language_code = data.get('language', 'en_US')
    components = data.get('components', [])

    if not recipient_id or not template_name:
        return jsonify({"error": "Missing recipient_id or template_name"}), 400

    try:
        # Create a log entry
        log = MessageLog(
            recipient=recipient_id,
            message_body=f"Template: {template_name}", 
            status='queued',
            message_type='whatsapp_template',
            sent_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        # Dispatch asynchronous task
        task = send_whatsapp_template_task.delay(
            recipient_id, 
            template_name, 
            language_code, 
            components,
            log.id
        )

        current_app.logger.info(f"Queued WhatsApp template '{template_name}' for {recipient_id}, Task ID: {task.id}")

        return jsonify({
            "status": "queued", 
            "task_id": task.id, 
            "log_id": log.id
        }), 202

    except Exception as e:
        current_app.logger.error(f"Error queuing WhatsApp message: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@whatsapp_bp.route('/send/text', methods=['POST'])
@limiter.limit("60 per minute")
def send_text():
    """
    Endpoint to trigger sending a WhatsApp text message.
    Payload:
    {
        "to": "1234567890",
        "text": "Hello there!"
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    recipient_id = data.get('to')
    text_body = data.get('text')

    if not recipient_id or not text_body:
        return jsonify({"error": "Missing recipient_id or text_body"}), 400

    try:
        # Create a log entry
        log = MessageLog(
            recipient=recipient_id,
            message_body=text_body,
            status='queued',
            message_type='whatsapp_text',
            sent_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        # Dispatch asynchronous task
        task = send_whatsapp_text_task.delay(recipient_id, text_body, log.id)

        current_app.logger.info(f"Queued WhatsApp text for {recipient_id}, Task ID: {task.id}")

        return jsonify({
            "status": "queued", 
            "task_id": task.id, 
            "log_id": log.id
        }), 202

    except Exception as e:
        current_app.logger.error(f"Error queuing WhatsApp message: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
