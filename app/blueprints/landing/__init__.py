from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.utils.tenant_context import get_current_school

landing_bp = Blueprint('landing', __name__, template_folder='templates')

@landing_bp.route('/')
def index():
    school = get_current_school()
    
    # Authenticated users should go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
        
    # Render the beautiful landing page for everyone else
    return render_template('landing/index.html', rays_machad_name=school.name if school else "Rays Tech")
