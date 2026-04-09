from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _

class GeneralSettingsForm(FlaskForm):
    rays_machad_name = StringField(_('Rays Machad Name'), validators=[DataRequired()])
    rays_machad_address = StringField(_('Address'))
    rays_machad_phone = StringField(_('Phone'))
    rays_machad_email = StringField(_('Email'))
    active_term = StringField(_('Active Academic Term'), validators=[DataRequired()])
    currency = StringField(_('System Currency'), default='USD')
    
    # WhatsApp Settings
    whatsapp_access_token = StringField(_('WhatsApp Access Token (Meta)'))
    whatsapp_phone_number_id = StringField(_('WhatsApp Phone Number ID'))
    whatsapp_mode = SelectField(_('Messaging Mode'), choices=[('live', _('Live (Sends real messages)')), ('mock', _('Mock (Development only)'))])
    
    # Grade Threshold Settings (Minimum %)
    grade_a_plus = IntegerField(_('Minimum for A+'), default=90)
    grade_a = IntegerField(_('Minimum for A'), default=80)
    grade_b_plus = IntegerField(_('Minimum for B+'), default=70)
    grade_b = IntegerField(_('Minimum for B'), default=60)
    grade_c_plus = IntegerField(_('Minimum for C+'), default=55)
    grade_c = IntegerField(_('Minimum for C'), default=50)
    grade_d = IntegerField(_('Minimum for D'), default=40)
    
    submit = SubmitField(_('Save Settings'))

class CategoryForm(FlaskForm):
    name = StringField(_('Category Name'), validators=[DataRequired()])
    type = SelectField(_('Category Type'), choices=[
        ('Subject', _('Curriculum / Subject')),
        ('Expense', _('Financial / Expense'))
    ], validators=[DataRequired()])
    description = StringField(_('Description'))
    submit = SubmitField(_('Save Category'))
