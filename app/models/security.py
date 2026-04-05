from app.extensions import db
from datetime import datetime


class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    __table_args__ = {'schema': 'madrasah_db'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('madrasah_db.users.id'), nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('madrasah_db.schools.id'), nullable=True)
    
    user = db.relationship('User', backref=db.backref('login_logs', lazy=True))
    school = db.relationship('School', backref=db.backref('login_logs', lazy=True))
    
    email = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False) # 'Success', 'Failed', 'Suspicious'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LoginLog {self.email} - {self.status}>'
