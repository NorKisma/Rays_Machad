from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
from flask_babel import lazy_gettext as _

class StudentRegistrationForm(FlaskForm):
    full_name = StringField(_('Full Name'), validators=[DataRequired(), Length(min=2, max=100)])
    
    enrollment_number = StringField(_('Enrollment Number'), validators=[DataRequired()])
    date_of_birth = DateField(_('Date of Birth'), format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField(_('Gender'), choices=[('Male', _('Male')), ('Female', _('Female'))], validators=[DataRequired()])
    
    # Parent/Guardian
    father_name = StringField(_("Father's Name"), validators=[DataRequired(), Length(max=100)])
    mother_name = StringField(_("Mother's Name"), validators=[Length(max=100)])
    parent_contact = StringField(_('Parent Contact'), validators=[DataRequired(), Length(min=10, max=15)])
    linked_parent = SelectField(_('Link to Parent Account'), coerce=int, validators=[Optional()])
    student_user = SelectField(_("Link to Student's User Account"), coerce=int, validators=[Optional()])
    address = StringField(_('Address'), validators=[Length(max=200)])

    # Academic
    student_class = SelectField(_('Assigned Class'), coerce=int, validators=[DataRequired()])
    hifz_status = SelectField(_('Hifz Status'), choices=[
        ('Nazira', _('Nazira (Reading)')),
        ('Hifz', _('Hifz (Memorization)')),
        ('Revision', _('Revision (Daur)'))
    ], default='Nazira')
    current_juz = SelectField(_('Current Juz'), choices=[(i, str(i)) for i in range(1, 31)], coerce=int, default=1)
    current_surah = StringField(_('Current Surah'), validators=[Optional(), Length(max=100)])
    current_aya = IntegerField(_('Current Aya'), validators=[Optional()], default=0)
    
    # Financials
    monthly_fee = DecimalField(_('Monthly Fee'), places=2, validators=[Optional()], default=0.00)
    
    status = SelectField(_('Status'), choices=[
        ('Active', _('Active')),
        ('Pending', _('Pending')),
        ('Inactive', _('Inactive'))
    ], default='Active')
    
    submit = SubmitField(_('Process Registration'))

    def __init__(self, *args, **kwargs):
        self.original_enrollment = kwargs.pop('original_enrollment', None)
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)

    def validate_enrollment_number(self, enrollment_number):
        if self.original_enrollment and enrollment_number.data == self.original_enrollment:
            return
            
        from app.models.student import Student
        student = Student.query.filter_by(enrollment_number=enrollment_number.data).first()
        if student:
            from wtforms import ValidationError
            raise ValidationError(_('This enrollment number is already in use. Please use a unique ID.'))