from app.extensions import db
from datetime import datetime

from app.models.mixins import SchoolContextMixin

class Announcement(db.Model, SchoolContextMixin):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.String(50), default='All') # All, Teachers, Students, Parents
    priority = db.Column(db.String(20), default='Normal') # Normal, High, Critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('Rays_machda.users.id'))
    
    author = db.relationship('User', backref='announcements')

    def __repr__(self):
        return f'<Announcement {self.title}>'
