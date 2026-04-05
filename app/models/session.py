from app.extensions import db
from datetime import datetime

from app.models.mixins import SchoolContextMixin

class ClassSession(db.Model, SchoolContextMixin):
    __tablename__ = 'class_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class_schedules.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False) # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50))
    
    # Relationship
    class_info = db.relationship('ClassSchedule', backref='sessions', lazy=True)

    def __repr__(self):
        return f'<ClassSession {self.day_of_week} {self.start_time}-{self.end_time}>'
