from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.utils.tenant_context import get_current_school

landing_bp = Blueprint('landing', __name__, template_folder='templates')

@landing_bp.route('/')
def index():
    school = get_current_school()
    
    # If a school is detected (subdomain/domain), redirect to their portal
    if school:
        if current_user.is_authenticated:
            return redirect(url_for("auth.dashboard"))
        return redirect(url_for("auth.login"))
        
    # No school (main domain) -> Redirect to Login for now
    return redirect(url_for('auth.login'))
