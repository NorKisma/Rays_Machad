from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class Teacher(db.Model, SchoolContextMixin):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    employee_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(100)) # e.g. Hifz, Tajwid, Arabic
    qualification = db.Column(db.String(100))
    monthly_salary = db.Column(db.Numeric(10, 2), default=0)
    joining_date = db.Column(db.Date, default=datetime.utcnow().date())
    status = db.Column(db.String(20), default='Active') # Active, Terminated, Resigned
    user_id = db.Column(db.Integer, db.ForeignKey('madrasah_db.users.id'), nullable=True)
    
    # Relationships
    teacher_account = db.relationship('User', foreign_keys=[user_id], backref=db.backref('teacher_profile', uselist=False), lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendances = db.relationship(
        'Attendance',
        backref='teacher',
        lazy=True
    )

    def __repr__(self):
        return f'<Teacher {self.full_name}>'
