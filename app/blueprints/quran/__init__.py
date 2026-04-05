from flask import Blueprint

quran_bp = Blueprint('quran', __name__, template_folder='templates')

from app.blueprints.quran import routes  # noqa
