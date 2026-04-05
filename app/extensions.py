from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from celery import Celery
from app.utils.tenant_query import TenantQuery

db = SQLAlchemy(query_class=TenantQuery)
migrate = Migrate()
login_manager = LoginManager()
babel = Babel()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()
celery = Celery()
csrf = CSRFProtect()