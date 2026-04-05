from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin

class Fee(db.Model, SchoolContextMixin):
    __tablename__ = 'fees'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), default=0)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # Tuition, Admission, Exam, etc.
    fee_month = db.Column(db.String(20)) # e.g., '2026-01'
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Unpaid')  # Unpaid, Paid, Partial
    payment_method = db.Column(db.String(50))  # Cash, Bank Transfer, E-paisa
    transaction_id = db.Column(db.String(100))
    remarks = db.Column(db.Text)

    # Relationship with Student
    student = db.relationship('Student', backref=db.backref('fees', cascade='all, delete-orphan', lazy='dynamic'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Fee {self.id} - Student {self.student_id} - {self.status}>'

class Expense(db.Model, SchoolContextMixin):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Salary, Rent, Utilities, Maintenance, etc.
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, default=datetime.utcnow().date)
    payment_method = db.Column(db.String(50), default='Cash')
    status = db.Column(db.String(20), default='Paid')  # Paid, Payable (Pending)
    transaction_id = db.Column(db.String(100))
    expense_month = db.Column(db.String(20)) # e.g., '2026-02'
    description = db.Column(db.Text)
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)
    
    # Optional relationship if categorized as Salary
    staff_member = db.relationship('Teacher', backref=db.backref('expenses', lazy='dynamic'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Expense {self.title} - {self.amount}>'
