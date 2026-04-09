# app.models.user.py
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class User(db.Model, UserMixin, SchoolContextMixin):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'Rays_machda'}
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Role: 'A' = Admin, 'T' = Teacher, 'S' = Staff, 'F' = Finance, 'P' = Parent, 'U' = Student (default)
    role = db.Column(db.String(10), nullable=False, default='U')
    is_active = db.Column(db.Boolean, default=True)
    
    # SaaS: Multi-tenancy
    school = db.relationship('School', backref=db.backref('users', lazy=True))
    
    # Tracking fields
    deleted_at = db.Column(db.DateTime, nullable=True) # Soft delete timestamp
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True) # Support for IPv6
    last_login_attempt = db.Column(db.DateTime, nullable=True)
    login_status = db.Column(db.String(20), nullable=True)

    def set_password(self, password):
        """Hashes the password using the default scrypt/pbkdf2."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the hash against the provided password."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def __repr__(self):
        return f'<User {self.email}>'

    def get_reset_token(self):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer as Serializer
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)


    @property
    def is_super_admin(self):
        """Checks if the user is a global SaaS system administrator."""
        from flask import current_app
        super_admins = current_app.config.get('SAAS_SUPER_ADMINS', ['nor.jws@gmail.com'])
        return self.email in super_admins

    @property
    def is_admin(self):
        return self.role in ['A', 'Admin']

    @property
    def is_teacher(self):
        return self.role == 'T'

    @property
    def is_staff(self):
        return self.role == 'S'

    @property
    def is_parent(self):
        return self.role == 'P'

    @property
    def is_student(self):
        return self.role == 'U'

    @property
    def is_user(self):
        return self.role == 'U'
    
    @property
    def is_finance(self):
        return self.role == 'F'
   
   
