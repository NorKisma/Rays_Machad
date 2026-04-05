from flask import Blueprint

saas_admin_bp = Blueprint('saas_admin', __name__, template_folder='templates')

from app.blueprints.saas_admin import routes
