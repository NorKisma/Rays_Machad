from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_babel import lazy_gettext as _

class AnnouncementForm(FlaskForm):
    title = StringField(_('Title'), validators=[DataRequired()])
    content = TextAreaField(_('Content'), validators=[DataRequired()])
    target_audience = SelectField(_('Target Audience'), choices=[
        ('All', _('Everyone')),
        ('Teachers', _('Teachers Only')),
        ('Students', _('Students Only')),
        ('Parents', _('Parents Only'))
    ], default='All')
    priority = SelectField(_('Priority'), choices=[
        ('Normal', _('Normal')),
        ('High', _('High')),
        ('Critical', _('Critical'))
    ], default='Normal')
    expires_at = DateTimeField(_('Expiry Date (Optional)'), format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField(_('Post Announcement'))
