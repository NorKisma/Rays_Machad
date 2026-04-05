# app/blueprints/exams/__init__.py
from flask import Blueprint

exams_bp = Blueprint('exams', __name__, url_prefix='/exams', template_folder='templates')

from app.blueprints.exams import routes
