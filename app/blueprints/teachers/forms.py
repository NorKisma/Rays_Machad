from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional
from flask_babel import lazy_gettext as _

class TeacherRegistrationForm(FlaskForm):
    full_name = StringField(_('Full Name'), validators=[DataRequired()])
    employee_number = StringField(_('Employee ID'), validators=[DataRequired()])
    email = StringField(_('Email Address'), validators=[DataRequired(), Email()])
    phone = StringField(_('Phone Number'))
    qualification = StringField(_('Qualification'))
    monthly_salary = StringField(_('Monthly Salary'), default='0')
    joining_date = DateField(_('Joining Date'), validators=[Optional()])
    status = SelectField(_('Status'), choices=[
        ('Active', _('Active')),
        ('Resigned', _('Resigned')),
        ('Terminated', _('Terminated'))
    ])
    linked_user = SelectField(_('Link to User Account'), coerce=int, validators=[Optional()])
    submit = SubmitField(_('Register Teacher'))
