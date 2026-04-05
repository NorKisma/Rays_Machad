from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_babel import lazy_gettext as _

from app.models.user import User

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField(_("Email"), validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(_("Password"), validators=[DataRequired(), Length(max=128)])
    remember = BooleanField(_("Remember me"))
    submit = SubmitField(_("Sign in"))

class RegisterForm(FlaskForm):
    name = StringField(_("Full Name"), validators=[DataRequired()])
    email = StringField(_("Email"), validators=[DataRequired(), Email()])
    role = SelectField(
        _("Role"),
        choices=[("A", _("Admin")), ("T", _("Teacher")), ("S", _("Staff")), ("F", _("Finance")), ("P", _("Parent")), ("U", _("Student"))],
        default="U"
    )
    password = PasswordField(_('Password'), validators=[
        DataRequired(), 
        Length(min=8, message=_("Password must be at least 8 characters."))
    ])
    confirm_password = PasswordField(_('Confirm Password'), validators=[
        DataRequired(), 
        EqualTo('password', message=_("Passwords must match."))
    ])
    submit = SubmitField(_('Create User'))

    def validate_email(self, email):
        if User.query.filter_by(email=email.data.lower()).first():
            raise ValidationError(_("Email already exists."))

class EditUserForm(FlaskForm):
    name = StringField(
        _("Full Name"),
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    email = StringField(
        _("Email"),
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    role = SelectField(
        _("Role"),
        choices=[('U', _('Student')), ('A', _('Admin')), ('T', _('Teacher')), ('S', _('Staff')), ('F', _('Finance')), ('P', _('Parent'))],
        validators=[DataRequired()]
    )
    submit = SubmitField(_("Update Changes"))

    def __init__(self, original_email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        """Ensure no other user has this email."""
        if email.data.lower() != self.original_email.lower():
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError(_("Email is already in use by another user."))

class ForgotPasswordForm(FlaskForm):
    email = StringField(_("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_("Request Password Reset"))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_("New Password"), validators=[
        DataRequired(), 
        Length(min=8, message=_("Password must be at least 8 characters."))
    ])
    confirm_password = PasswordField(_("Confirm New Password"), validators=[
        DataRequired(), 
        EqualTo('password', message=_("Passwords must match."))
    ])
    submit = SubmitField(_("Reset Password"))

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_("Current Password"), validators=[DataRequired()])
    new_password = PasswordField(_("New Password"), validators=[
        DataRequired(), 
        Length(min=8, message=_("Password must be at least 8 characters."))
    ])
    confirm_password = PasswordField(_("Confirm New Password"), validators=[
        DataRequired(), 
        EqualTo('new_password', message=_("Passwords must match."))
    ])
    submit = SubmitField(_("Update Password"))

class VerifyOTPForm(FlaskForm):
    """Form for OTP verification."""
    otp = StringField(_("OTP Code"), validators=[
        DataRequired(), 
        Length(min=6, max=6, message=_("OTP must be 6 digits."))
    ])
    submit = SubmitField(_("Verify OTP"))

class ResetPasswordWithOTPForm(FlaskForm):
    """Form for resetting password after OTP verification."""
    password = PasswordField(_("New Password"), validators=[
        DataRequired(), 
        Length(min=8, message=_("Password must be at least 8 characters."))
    ])
    confirm_password = PasswordField(_("Confirm New Password"), validators=[
        DataRequired(), 
        EqualTo('password', message=_("Passwords must match."))
    ])
    submit = SubmitField(_("Reset Password"))
