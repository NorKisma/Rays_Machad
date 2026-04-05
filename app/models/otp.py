# app/models/otp.py
from app.extensions import db
from datetime import datetime, timedelta
import secrets
import string
from app.models.mixins import SchoolContextMixin

class OTP(db.Model, SchoolContextMixin):
    __tablename__ = 'otps'
    __table_args__ = {'schema': 'madrasah_db'}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('madrasah_db.users.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False, default='password_reset')  # password_reset, login, etc
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='otps')
    
    @staticmethod
    def generate_code(length=6):
        """Generate a random numeric OTP code"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    @staticmethod
    def create_otp(user_id, purpose='password_reset', expiry_minutes=10):
        """Create a new OTP for a user"""
        # Invalidate any existing unused OTPs for this user and purpose
        OTP.query.filter_by(
            user_id=user_id, 
            purpose=purpose, 
            is_used=False
        ).update({'is_used': True})
        db.session.commit()
        
        # Create new OTP
        code = OTP.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        otp = OTP(
            user_id=user_id,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        db.session.add(otp)
        db.session.commit()
        
        return otp
    
    @staticmethod
    def verify_otp(user_id, code, purpose='password_reset'):
        """Verify an OTP code for a user"""
        otp = OTP.query.filter_by(
            user_id=user_id,
            code=code,
            purpose=purpose,
            is_used=False
        ).first()
        
        if not otp:
            return False, "Invalid OTP code"
        
        if datetime.utcnow() > otp.expires_at:
            return False, "OTP has expired"
        
        # Mark OTP as used
        otp.is_used = True
        db.session.commit()
        
        return True, "OTP verified successfully"
    
    def __repr__(self):
        return f'<OTP {self.code} for User {self.user_id}>'
