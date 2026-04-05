from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Optional
from flask_babel import lazy_gettext as _

class ClassForm(FlaskForm):
    class_name = StringField(_('Class Name'), validators=[DataRequired()])
    description = TextAreaField(_('Description'))
    teacher_id = SelectField(_('Main Teacher'), coerce=int, validators=[DataRequired()])

    submit = SubmitField(_('Save Class'))
class ClassSessionForm(FlaskForm):
    day_of_week = SelectField(_('Day of Week'), choices=[
        ('Monday', _('Monday')), ('Tuesday', _('Tuesday')), ('Wednesday', _('Wednesday')),
        ('Thursday', _('Thursday')), ('Friday', _('Friday')), ('Saturday', _('Saturday')), ('Sunday', _('Sunday'))
    ], validators=[DataRequired()])
    start_time = StringField(_('Start Time (HH:MM)'), validators=[DataRequired()])
    end_time = StringField(_('End Time (HH:MM)'), validators=[DataRequired()])
    room = StringField(_('Room/Location'))
    submit = SubmitField(_('Add Session'))

class SubjectForm(FlaskForm):
    name = StringField(_('Subject Name'), validators=[DataRequired()])
    code = StringField(_('Subject Code'), validators=[Optional()])
    category = SelectField(_('Category'), choices=[
        ('Quranic', _('Quranic')),
        ('Arabic', _('Arabic')),
        ('Islamic Studies', _('Islamic Studies')),
        ('General', _('General Literacy')),
        ('Other', _('Other'))
    ], validators=[DataRequired()])
    description = TextAreaField(_('Description'), validators=[Optional()])
    submit = SubmitField(_('Save Subject'))
