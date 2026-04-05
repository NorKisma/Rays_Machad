from flask import Blueprint

financials_bp = Blueprint('financials', __name__, template_folder='templates')

from . import routes
