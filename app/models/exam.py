from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class Exam(db.Model, SchoolContextMixin):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(200), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # Hifz, Tajweed, Islamic Studies, General
    class_id = db.Column(db.Integer, db.ForeignKey('class_schedules.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    total_marks = db.Column(db.Integer, default=100)
    passing_marks = db.Column(db.Integer, default=50)
    
    # For Hifz exams
    surah_from = db.Column(db.String(100), nullable=True)
    surah_to = db.Column(db.String(100), nullable=True)
    juz_number = db.Column(db.Integer, nullable=True)
    
    # Metadata
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Ongoing, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_assigned = db.relationship('ClassSchedule', backref='exams')
    subject = db.relationship('Subject', backref='exams')
    teacher = db.relationship('Teacher', backref='exams')
    results = db.relationship('ExamResult', backref='exam', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Exam {self.exam_name}>'


class ExamResult(db.Model, SchoolContextMixin):
    __tablename__ = 'exam_results'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Marks
    marks_obtained = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(10), nullable=True)  # A+, A, B+, B, C, D, F
    
    # For Hifz/Tajweed specific evaluation
    memorization_accuracy = db.Column(db.Integer, nullable=True)  # Percentage
    tajweed_score = db.Column(db.Integer, nullable=True)  # Percentage
    fluency_score = db.Column(db.Integer, nullable=True)  # Percentage
    
    # Status
    status = db.Column(db.String(20), default='Pass')  # Pass, Fail, Absent, Pending
    remarks = db.Column(db.Text, nullable=True)
    evaluated_by = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    evaluated_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('exam_results', lazy='dynamic'))
    evaluator = db.relationship('Teacher', foreign_keys=[evaluated_by])
    
    def calculate_grade(self, total_marks):
        """Calculate grade based on percentage"""
        if self.marks_obtained is None:
            return None
        
        percentage = (self.marks_obtained / total_marks) * 100
        
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'
    
    def __repr__(self):
        return f'<ExamResult Student:{self.student_id} Exam:{self.exam_id}>'
