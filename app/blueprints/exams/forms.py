# app/blueprints/exams/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, IntegerField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_babel import lazy_gettext as _

class ExamForm(FlaskForm):
    exam_name = StringField(_('Exam Name'), validators=[DataRequired()])
    exam_type = SelectField(_('Exam Type'), choices=[], validators=[DataRequired()])
    class_id = SelectField(_('Class'), coerce=int, validators=[Optional()])
    subject_id = SelectField(_('Subject'), coerce=int, validators=[Optional()])
    teacher_id = SelectField(_('Examiner/Teacher'), coerce=int, validators=[DataRequired()])
    exam_date = DateField(_('Exam Date'), validators=[DataRequired()])
    total_marks = IntegerField(_('Total Marks'), default=100, validators=[DataRequired(), NumberRange(min=1)])
    passing_marks = IntegerField(_('Passing Marks'), default=50, validators=[DataRequired(), NumberRange(min=1)])
    
    # For Hifz exams
    surah_from = StringField(_('Surah From'), validators=[Optional()])
    surah_to = StringField(_('Surah To'), validators=[Optional()])
    juz_number = IntegerField(_('Juz Number'), validators=[Optional(), NumberRange(min=1, max=30)])
    
    description = TextAreaField(_('Description'), validators=[Optional()])
    status = SelectField(_('Status'), choices=[
        ('Scheduled', _('Scheduled')),
        ('Ongoing', _('Ongoing')),
        ('Completed', _('Completed')),
        ('Cancelled', _('Cancelled'))
    ], default='Scheduled', validators=[DataRequired()])
    submit = SubmitField(_('Create Exam'))


class ExamResultForm(FlaskForm):
    marks_obtained = FloatField(_('Marks Obtained'), validators=[Optional(), NumberRange(min=0)])
    
    # For Hifz/Tajweed evaluation
    memorization_accuracy = IntegerField(_('Memorization Accuracy (%)'), validators=[Optional(), NumberRange(min=0, max=100)])
    tajweed_score = IntegerField(_('Tajweed Score (%)'), validators=[Optional(), NumberRange(min=0, max=100)])
    fluency_score = IntegerField(_('Fluency Score (%)'), validators=[Optional(), NumberRange(min=0, max=100)])
    
    status = SelectField(_('Status'), choices=[
        ('Excellent', _('Excellent')),
        ('Very Good', _('Very Good')),
        ('Good', _('Good')),
        ('Pass', _('Pass')),
        ('Fail', _('Fail')),
        ('Absent', _('Absent')),
        ('Pending', _('Pending'))
    ], validators=[DataRequired()])
    
    remarks = TextAreaField(_('Remarks'), validators=[Optional()])
    submit = SubmitField(_('Save Result'))
