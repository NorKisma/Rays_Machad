from app.extensions import db
from datetime import datetime
from datetime import date

from app.models.mixins import SchoolContextMixin

class Attendance(db.Model, SchoolContextMixin):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True) 
    class_id = db.Column(db.Integer, db.ForeignKey('class_schedules.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    period = db.Column(db.Integer, default=1)  # Maalintii 1, 2, 3, 4, etc.
    attendance_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='Present')  # Present, Absent, Late, Excused
    remarks = db.Column(db.Text)
    
    # Relationships
    class_assigned = db.relationship('ClassSchedule', backref='attendances', lazy=True, overlaps="attendances")
    subject = db.relationship('Subject', backref='attendances', lazy=True)
    # Marking teacher is already handled by the backref 'teacher' in Teacher model
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.attendance_date} - {self.status}>'
