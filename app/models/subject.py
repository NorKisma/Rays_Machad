from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class Subject(db.Model, SchoolContextMixin):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20)) # e.g. TWH01
    description = db.Column(db.Text)
    category = db.Column(db.String(50)) # e.g. Quranic, Arabic, General

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Subject {self.name}>'
