from flask import redirect, url_for, flash
from functools import wraps
from flask_login import current_user
from flask import abort
from flask_babel import _

from app.models.user import User   # ✅ import your User model


def permission_required(module):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models.permission import RolePermission
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            
            if not RolePermission.check(current_user.role, module):
                flash(_("You do not have permission to access this section."), "danger")
                return redirect(url_for("auth.dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['A', 'Admin']:
            flash(_("Administrative privileges required."), "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['A', 'S', 'F']:
            flash(_("Management privileges required."), "danger")
            return redirect(url_for("auth.dashboard"))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['A', 'S', 'T', 'F']:
            flash(_("Teacher or staff access required."), "danger")
            return redirect(url_for("auth.dashboard"))
        return f(*args, **kwargs)
    return decorated_function

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['A', 'S', 'P', 'F']:
            flash(_("Parent or staff access required."), "danger")
            return redirect(url_for("auth.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
