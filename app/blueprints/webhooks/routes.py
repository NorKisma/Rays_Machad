from flask import request, jsonify, current_app
from app.blueprints.webhooks import webhooks_bp
from app.models.message_log import MessageLog
from app.extensions import db
from datetime import datetime

@webhooks_bp.route('/textbee/sms', methods=['POST'])
def receive_textbee_sms():
    """
    Handle incoming SMS from TextBee Webhook.
    Docs mention generic payload, so we log it first.
    Expected fields: 'sender', 'message', 'timestamp' (or similar).
    """
    data = request.get_json(silent=True)
    if not data:
        current_app.logger.warning("Received TextBee webhook with no JSON data")
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    current_app.logger.info(f"Received TextBee SMS Payload: {data}")

    # Auto-detect fields based on common webhook patterns
    # TextBee might use: 'sender', 'from', 'phoneNumber', 'recipient' (if forwarded from device)
    sender = data.get('sender') or data.get('from') or data.get('phoneNumber')
    message_body = data.get('message') or data.get('text') or data.get('body') or data.get('content')
    
    if sender and message_body:
        # Log to DB as 'received' message
        msg_log = MessageLog(
            recipient=sender,  # In this context, recipient field stores the SENDER
            message_body=message_body,
            status='received',
            message_type='sms_inbound',
            sent_at=datetime.utcnow()
        )
        try:
            db.session.add(msg_log)
            db.session.commit()
            current_app.logger.info(f"Logged incoming SMS from {sender}")
        except Exception as e:
            current_app.logger.error(f"Failed to save incoming SMS: {e}")
            return jsonify({"status": "error", "message": "Database error"}), 500
            
    return jsonify({"status": "success", "message": "Received"}), 200

# WhatsApp Webhook (Optional/Future)
@webhooks_bp.route('/whatsapp', methods=['POST', 'GET'])
def receive_whatsapp():
    # Verification challenge (GET)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        my_token = current_app.config.get('WHATSAPP_VERIFY_TOKEN')
        if mode and token:
            if mode == 'subscribe' and token == my_token:
                return challenge, 200
            else:
                return 'Verification failed', 403
                
    # Incoming message (POST)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "ignored"}), 200

    current_app.logger.info(f"WhatsApp Webhook Payload: {data}")

    try:
        entries = data.get('entry', [])
        for entry in entries:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # 1. Handle Status Updates (sent, delivered, read, failed)
                statuses = value.get('statuses', [])
                for status in statuses:
                    wamid = status.get('id')
                    new_status = status.get('status')
                    
                    # Update DB if we track this message
                    # We need provider_message_id column in MessageLog
                    try:
                        log = MessageLog.query.filter_by(provider_message_id=wamid).first()
                        if log:
                            log.status = new_status
                            if new_status == 'failed':
                                # Extract errors title/detail
                                errors = status.get('errors', [])
                                log.error_message = str(errors)
                            
                            db.session.commit()
                            current_app.logger.info(f"Updated Message {wamid} Status: {new_status}")
                    except Exception as db_err:
                        current_app.logger.error(f"DB Error updating status for {wamid}: {db_err}")

                # 2. Handle Incoming Messages
                messages = value.get('messages', [])
                for msg in messages:
                    sender = msg.get('from')
                    msg_id = msg.get('id')
                    
                    # Prevent duplicate logging
                    if MessageLog.query.filter_by(provider_message_id=msg_id).first():
                        continue
                        
                    msg_type = msg.get('type')
                    body = "Media/Other"
                    if msg_type == 'text':
                        body = msg.get('text', {}).get('body')
                    elif msg_type == 'button':
                        body = f"Button: {msg.get('button', {}).get('text')}"
                    
                    log = MessageLog(
                        recipient=sender, # For inbound, recipient field holds the sender number
                        message_body=body,
                        status='received',
                        message_type='whatsapp_inbound',
                        provider_message_id=msg_id,
                        sent_at=datetime.utcnow()
                    )
                    db.session.add(log)
                    db.session.commit()
                    current_app.logger.info(f"Logged incoming WhatsApp from {sender}")

    except Exception as e:
        current_app.logger.error(f"Error processing WhatsApp webhook: {e}")
        # Return 200 to prevent Meta from retrying indefinitely
        return jsonify({"status": "error", "error": str(e)}), 200

    return jsonify({"status": "received"}), 200

@webhooks_bp.route('/ipay/callback', methods=['POST'])
def receive_ipay_callback():
    """
    Handle callback from WaafiPay (iPay) after user completes payment.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400

    current_app.logger.info(f"iPay Callback Received: {data}")

    # WaafiPay usually returns: transactionId, requestId, state (SUCCEEDED/FAILED)
    # The requestId corresponds to our internal transaction reference
    transaction_id = data.get('transactionId')
    request_id = data.get('requestId')
    state = data.get('state') # e.g., 'SUCCEEDED', 'FAILED'

    if request_id:
        from app.models.school import School
        school = School.query.filter_by(payment_transaction_id=request_id).first()
        
        if school:
            if state == 'SUCCEEDED':
                school.last_payment_status = 'Confirmed'
                # Do NOT auto-activate if human check is required, 
                # but we can set status to 'Pending Approval' or similar
                # For now, we'll mark it as paid.
                current_app.logger.info(f"Payment SUCCEEDED for school: {school.name}")
            else:
                school.last_payment_status = 'Failed'
                current_app.logger.warning(f"Payment FAILED for school: {school.name}")
            
            db.session.commit()
            return jsonify({"status": "processed"}), 200

    return jsonify({"status": "ignored"}), 200
