# __init__.py
import os
import importlib
from datetime import datetime
from flask import Flask, redirect, url_for, request, session
from flask_login import current_user
from dotenv import load_dotenv

from app.config import Config
from app.extensions import db, migrate, login_manager, babel, mail, celery, csrf
def create_app(config_class=Config):
    # Load .env variables
    load_dotenv()

    app = Flask(__name__)
    
    # Apply ProxyFix for SaaS environment
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config.from_object(config_class)

    # Ensure SQLALCHEMY_DATABASE_URI is set
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if not db_uri:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI not set in environment")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    from app.extensions import limiter, talisman
    limiter.init_app(app)

    # Talisman (Security headers)
    csp = {
        'default-src': ["'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com",
                        "https://fonts.googleapis.com", "https://fonts.gstatic.com",
                        "https://code.jquery.com", "https://cdn.datatables.net"],
        'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com", "data:"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", 
                      "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com",
                      "https://cdn.datatables.net"],
        'img-src': ["'self'", "data:", "https://www.transparenttextures.com", "https://*.googleusercontent.com"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", 
                       "https://cdnjs.cloudflare.com", "https://code.jquery.com", 
                       "https://cdn.datatables.net"]
    }
    talisman.init_app(app, content_security_policy=csp, force_https=False)
    
    # Configure Celery
    celery.conf.update(app.config)
    
    # Celery Beat Schedule
    from celery.schedules import crontab
    celery.conf.beat_schedule = {
        'daily-cleanup-60-days': {
            'task': 'app.tasks.cleanup_deleted_entities',
            'schedule': crontab(hour=0, minute=0), # Run every day at midnight
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    # Babel locale selector
    def get_locale():
        lang = session.get('lang')
        if lang:
            return lang
        match = request.accept_languages.best_match(app.config.get('LANGUAGES', ['en', 'ar', 'so']))
        return match if match else 'en'
    babel.init_app(app, locale_selector=get_locale)
    
    # SaaS Tenant Identification
    from app.utils.tenant_context import get_current_school
    from flask_login import logout_user
    from sqlalchemy import text
    @app.before_request
    def handle_tenant():
        # Identify school from subdomain
        school = get_current_school()
        
        # --- PHYSICAL DATABASE SWITCH ---
        # We assume the user 'rays_machad_admin' has access to all tenant databases
        if school:
            if not school.is_active or school.status == 'Suspended':
                from flask import render_template_string
                return render_template_string("<h1>School Suspended</h1><p>This school's account is currently suspended. Please contact support.</p>"), 403
                
            db_name = f"`rays_machad_tenant_{school.subdomain}`"
            try:
                # Ensure the connection is using the correct database context for business data
                db.session.execute(text(f"USE {db_name}"))
                app.logger.info(f"Tenant Switch: Subdomain={school.subdomain} -> Database={db_name}")
            except Exception as e:
                # If database doesn't exist yet, it's a critical setup issue
                app.logger.error(f"FATAL: Database {db_name} missing for school {school.name}")
                from flask import render_template_string
                return render_template_string("<h1>Setup Pending</h1><p>This school's database is being prepared. Please try again in a few minutes.</p>"), 503
        else:
            # Explicitly switch back to main DB for landing page/admin tools
            db.session.execute(text("USE `Rays_machda`"))
            app.logger.debug("Main DB Switch: Database=Rays_machda")

        # Security: Prevent Cross-Tenant access
        if current_user.is_authenticated:
            # Master Admin can see everything
            if not current_user.is_super_admin:
                if school:
                    if current_user.school_id != school.id:
                        app.logger.warning(f"SECURITY: User {current_user.email} (School {current_user.school_id}) tried to access Tenant {school.name} ({school.id})")
                        logout_user()
                        from flask import flash
                        flash("You do not have permission to access this school's portal.", "danger")
                        return redirect(url_for('auth.login'))
                else:
                    # Logged in but no school context (Main Domain)
                    if hasattr(current_user, 'school_id') and current_user.school_id:
                        # Redirect regular users to their own school subdomain
                        main_domain = os.environ.get('MAIN_DOMAIN', 'raystechcenter.online')
                        return redirect(f"https://{current_user.school.subdomain}.{main_domain}{request.path}")
                    else:
                        logout_user()
                        return redirect(url_for('auth.login'))
        
        # Redirect truly invalid subdomains to main page, but allow the main 'machad' domain
        host_main = request.host.split('.')[0]
        if host_main not in ['raystech', 'raystechcenter', 'machad', '161', 'localhost', 'www', '127'] and not school:
             return redirect("https://raystechcenter.online")

    # Context processor
    @app.context_processor
    def inject_conf_var():
        from app.models.setting import SystemSetting
        from app.models.permission import RolePermission
        from app.models.fee import Expense
        from flask import g, current_app
        
        school = get_current_school()
        
        # Identify the system type for feature toggling
        system_type = current_app.config.get('SYSTEM_TYPE', 'madrasah')
        if school:
            if school.subdomain == 'ray_machad':
                system_type = 'ray_machad'
            elif school.subdomain == 'somcoffe':
                system_type = 'somcoffe'
            else:
                system_type = 'tenant'
        
        # Override settings with school-specific values if applicable
        m_name = school.name if school else SystemSetting.get_setting('rays_machad_name', 'Rays Machad')
        
        from app.models.subject import Subject
        from app.models.class_schedule import ClassSchedule

        return dict(
            get_locale=get_locale,
            current_school=school,
            rays_machad_name=m_name,
            rays_machad_phone=SystemSetting.get_setting('rays_machad_phone', '+252...'),
            rays_machad_address=SystemSetting.get_setting('rays_machad_address', 'Main Office'),
            system_type=system_type,
            now=datetime.utcnow(),
            db=db,
            RolePermission=RolePermission,
            Expense=Expense,
            Subject=Subject,
            ClassSchedule=ClassSchedule
        )

    # Flask-Login settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # Import models for migrations
    with app.app_context():
        from app import models

    # Auto-register blueprints
    blueprints_folder = os.path.join(app.root_path, "blueprints")
    for module_name in sorted(os.listdir(blueprints_folder)):
        module_path = os.path.join(blueprints_folder, module_name)
        if os.path.isdir(module_path) and "__init__.py" in os.listdir(module_path):
            try:
                bp_mod_path = f"app.blueprints.{module_name}"
                bp_mod = importlib.import_module(bp_mod_path)

                found_bp = None
                for attr in dir(bp_mod):
                    obj = getattr(bp_mod, attr)
                    from flask import Blueprint
                    if isinstance(obj, Blueprint) and attr.endswith("_bp"):
                        found_bp = obj
                        break

                # Try routes.py if not found
                if not found_bp:
                    try:
                        routes_mod = importlib.import_module(f"{bp_mod_path}.routes")
                        for attr in dir(routes_mod):
                            obj = getattr(routes_mod, attr)
                            if isinstance(obj, Blueprint) and attr.endswith("_bp"):
                                found_bp = obj
                                break
                    except ImportError:
                        pass

                # Register blueprint
                if found_bp and found_bp.name not in app.blueprints:
                    url_prefix = f"/{module_name}"
                    if module_name == 'landing':
                        url_prefix = None # Register at root
                    app.register_blueprint(found_bp, url_prefix=url_prefix)
                    app.logger.info(f"Registered blueprint: {found_bp.name} at {url_prefix}")
            except Exception as e:
                app.logger.exception(f"Error registering blueprint {module_name}: {e}")

    # Language switcher
    @app.route('/set_language/<lang>')
    def set_language(lang):
        if lang in app.config.get('LANGUAGES', []):
            session['lang'] = lang
        else:
            app.logger.warning(f"Attempted to set unsupported language: {lang}")
        return redirect(request.referrer or url_for('index'))
    
    @app.route('/sw.js')
    def serve_sw():
        return app.send_static_file('sw.js')

    @app.route('/manifest.json')
    def serve_manifest():
        return app.send_static_file('site.webmanifest')

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template("429.html"), 429

    from . import tasks

    return app
