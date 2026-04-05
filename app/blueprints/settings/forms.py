from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _

class GeneralSettingsForm(FlaskForm):
    madrasah_name = StringField(_('Madrasah Name'), validators=[DataRequired()])
    madrasah_address = StringField(_('Address'))
    madrasah_phone = StringField(_('Phone'))
    madrasah_email = StringField(_('Email'))
    active_term = StringField(_('Active Academic Term'), validators=[DataRequired()])
    currency = StringField(_('System Currency'), default='USD')
    
    # WhatsApp Settings
    whatsapp_access_token = StringField(_('WhatsApp Access Token (Meta)'))
    whatsapp_phone_number_id = StringField(_('WhatsApp Phone Number ID'))
    whatsapp_mode = SelectField(_('Messaging Mode'), choices=[('live', _('Live (Sends real messages)')), ('mock', _('Mock (Development only)'))])
    
    submit = SubmitField(_('Save Settings'))

class CategoryForm(FlaskForm):
    name = StringField(_('Category Name'), validators=[DataRequired()])
    type = SelectField(_('Category Type'), choices=[
        ('Subject', _('Curriculum / Subject')),
        ('Expense', _('Financial / Expense'))
    ], validators=[DataRequired()])
    description = StringField(_('Description'))
    submit = SubmitField(_('Save Category'))
