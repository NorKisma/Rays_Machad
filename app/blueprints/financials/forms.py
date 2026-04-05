from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_babel import lazy_gettext as _

class FeeForm(FlaskForm):
    student_id = SelectField(_('Student'), coerce=int, validators=[DataRequired()])
    amount = DecimalField(_('Amount'), validators=[DataRequired()])
    fee_type = SelectField(_('Fee Type'), choices=[
        ('Tuition', _('Tuition Fee')),
        ('Admission', _('Admission Fee')),
        ('Exam', _('Exam Fee')),
        ('Uniform', _('Uniform Fee')),
        ('Books', _('Books Fee')),
        ('Bus', _('Transport / Bus')),
        ('Activity', _('Extra Activity')),   
        ('Library', _('Library Fee')),
        
        ('Other', _('Other'))
    ], validators=[DataRequired()])
    fee_month = StringField(_('Fee Month'), validators=[Optional()], description="e.g. 2026-01")
    due_date = DateField(_('Due Date'), validators=[DataRequired()])
    remarks = TextAreaField(_('Remarks'), validators=[Optional()])
    submit = SubmitField(_('Save Fee'))

class PaymentForm(FlaskForm):
    amount_paid = DecimalField(_('Amount Paid'), validators=[DataRequired()])
    payment_date = DateField(_('Payment Date'), validators=[DataRequired()])
    payment_method = SelectField(_('Payment Method'), choices=[
        ('Cash', _('Cash')),
        ('Bank Transfer', _('Bank Transfer')),
        ('E-paisa', _('E-paisa')),
        ('Check', _('Check'))
    ], validators=[DataRequired()])
    transaction_id = StringField(_('Transaction ID'), validators=[Optional()])
    remarks = TextAreaField(_('Remarks'), validators=[Optional()])
    submit = SubmitField(_('Record Payment'))

class ExpenseForm(FlaskForm):
    title = StringField(_('Title'), validators=[DataRequired()])
    category = SelectField(_('Category'), choices=[
        ('Salary', _('Salary')),
        ('Rent', _('Rent')),
        ('Utilities', _('Utilities')),
        ('Maintenance', _('Maintenance')),
        ('Supplies', _('Supplies')),
        ('Other', _('Other'))
    ], validators=[DataRequired()])
    amount = DecimalField(_('Amount'), validators=[DataRequired()])
    expense_date = DateField(_('Expense Date'), validators=[DataRequired()])
    payment_method = SelectField(_('Payment Method'), choices=[
        ('Cash', _('Cash')),
        ('Bank Transfer', _('Bank Transfer')),
        ('Check', _('Check'))
    ], validators=[DataRequired()])
    status = SelectField(_('Status'), choices=[
        ('Paid', _('Paid')),
        ('Payable', _('Payable (Pending)'))
    ], default='Paid', validators=[DataRequired()])
    teacher_id = SelectField(_('Payee (Staff/Teacher)'), coerce=int, validators=[Optional()])
    description = TextAreaField(_('Description'), validators=[Optional()])
    submit = SubmitField(_('Record Expense'))
