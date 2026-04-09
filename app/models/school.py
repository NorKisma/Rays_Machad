from app.extensions import db
from datetime import datetime

class School(db.Model):
    __tablename__ = 'schools'
    __table_args__ = {'schema': 'Rays_machda'}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subdomain = db.Column(db.String(50), unique=True, nullable=False)
    domain = db.Column(db.String(120), unique=True, nullable=True)
    
    # Settings & Status
    is_active = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Active, Suspended
    subscription_plan = db.Column(db.String(20), default='Basic') # Basic, Pro, Enterprise
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Contact Info
    admin_email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Payment Info
    payment_transaction_id = db.Column(db.String(100), nullable=True)
    payment_phone = db.Column(db.String(20), nullable=True)
    requested_amount = db.Column(db.Numeric(10, 2), nullable=True)
    last_payment_status = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True) # Soft delete timestamp
    
    def __repr__(self):
        return f"<School {self.subdomain}>"

    @staticmethod
    def get_by_subdomain(subdomain):
        return School.query.filter_by(subdomain=subdomain, is_active=True).first()
