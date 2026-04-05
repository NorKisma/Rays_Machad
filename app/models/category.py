from app.extensions import db
from datetime import datetime

from app.models.mixins import SchoolContextMixin

class Category(db.Model, SchoolContextMixin):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False) # 'Subject', 'Expense'
    description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('name', 'type', name='uix_name_type'),)

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'
