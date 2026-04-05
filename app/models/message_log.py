from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class MessageLog(db.Model, SchoolContextMixin):
    __tablename__ = 'message_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(20), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='sent') # sent, failed
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.String(50)) # monthly_report, announcement
    provider_message_id = db.Column(db.String(100), unique=True, nullable=True) # wamid
    
    def __repr__(self):
        return f'<MessageLog {self.recipient} - {self.status}>'
