from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class Student(db.Model, SchoolContextMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False, index=True)
    enrollment_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # Personal Details
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # Male, Female

    # Parent / Guardian Details
    father_name = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    parent_contact = db.Column(db.String(20), nullable=False, index=True)
    address = db.Column(db.Text)

    # Academic / Madrasah Details
    current_juz = db.Column(db.Integer, default=1)
    current_surah = db.Column(db.String(100))
    current_aya = db.Column(db.Integer, default=0)
    hifz_status = db.Column(db.String(20), default='Nazira')  # Nazira, Hifz, Revision
    
    # Financials
    monthly_fee = db.Column(db.Numeric(10, 2), default=0.00)

    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Graduated
    class_id = db.Column(db.Integer, db.ForeignKey('class_schedules.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('madrasah_db.users.id'), nullable=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('madrasah_db.users.id'), nullable=True)
    
    # Relationships
    class_assigned = db.relationship('ClassSchedule', backref='students', lazy=True)
    parent = db.relationship('User', foreign_keys=[parent_id], backref='children', lazy=True)
    student_account = db.relationship('User', foreign_keys=[student_user_id], backref=db.backref('student_profile', uselist=False), lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendances = db.relationship(
        'Attendance',
        backref='student',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Student {self.full_name}>'
