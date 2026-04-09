from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class_subjects = db.Table('class_subjects',
    db.Column('class_id', db.Integer, db.ForeignKey('class_schedules.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)

class ClassSchedule(db.Model, SchoolContextMixin):
    __tablename__ = 'class_schedules'

    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True) # Kept for backwards compatibility just in case
    tuition_fee = db.Column(db.Numeric(10, 2), default=0.00)
    admission_fee = db.Column(db.Numeric(10, 2), default=0.00)
    exam_fee = db.Column(db.Numeric(10, 2), default=0.00)
    uniform_fee = db.Column(db.Numeric(10, 2), default=0.00)
    books_fee = db.Column(db.Numeric(10, 2), default=0.00)
    bus_fee = db.Column(db.Numeric(10, 2), default=0.00)
    activity_fee = db.Column(db.Numeric(10, 2), default=0.00)
    library_fee = db.Column(db.Numeric(10, 2), default=0.00)
    other_fee = db.Column(db.Numeric(10, 2), default=0.00)

    @property
    def total_fees(self):
        return (self.tuition_fee or 0) + (self.admission_fee or 0) + (self.exam_fee or 0) + (self.uniform_fee or 0) + \
               (self.books_fee or 0) + (self.bus_fee or 0) + (self.activity_fee or 0) + \
               (self.library_fee or 0) + (self.other_fee or 0)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='classes', lazy=True)
    subjects = db.relationship('Subject', secondary=class_subjects, lazy='subquery', backref=db.backref('classes', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ClassSchedule {self.class_name}>'

