from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from app.blueprints.saas_admin import saas_admin_bp
from app.models.school import School
from app.models.user import User
from app.extensions import db
from app.utils.email_service import EmailService
from functools import wraps
import secrets
import string

def saas_super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email != 'nor.jws@gmail.com':
            flash("Unauthorized access.", "danger")
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function



@saas_admin_bp.route("/schools/add", methods=["GET", "POST"])
@login_required
@saas_super_admin_required
def add_school():
    if request.method == "POST":
        name = request.form.get("name")
        subdomain = request.form.get("subdomain").lower().strip()
        admin_email = request.form.get("admin_email")
        payment_phone = request.form.get("payment_phone")
        requested_amount = request.form.get("requested_amount")
        
        if School.query.filter_by(subdomain=subdomain).first():
            flash("Subdomain already exists!", "danger")
        else:
            new_school = School(
                name=name,
                subdomain=subdomain,
                admin_email=admin_email,
                payment_phone=payment_phone,
                requested_amount=requested_amount,
                is_active=True
            )
            db.session.add(new_school)
            db.session.commit()
            flash(f"School '{name}' created successfully!", "success")
            return redirect(url_for('saas_admin.list_schools'))

    return render_template("saas_admin/add_school.html")

@saas_admin_bp.route("/schools/approve/<int:id>")
@login_required
@saas_super_admin_required
def approve_school(id):
    """Approve a pending school: Activate it, generate a password, and send credentials via email."""
    school = School.query.get_or_404(id)
    
    if school.is_active and school.status == 'Active':
        flash(f"School '{school.name}' is already active!", "info")
        return redirect(url_for('saas_admin.list_schools'))
    
    # Generate a new random password for the admin
    new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
    
    # Ensure the admin user exists for this school
    admin_user = User.query.filter_by(email=school.admin_email).first()
    
    if not admin_user:
        # Create the admin user if doesn't exist
        admin_user = User(
            name=f"{school.name} Admin",
            email=school.admin_email,
            role='A',
            school_id=school.id,
            is_active=True
        )
        db.session.add(admin_user)
        current_app.logger.info(f"Created new admin user for {school.name}: {school.admin_email}")
    else:
        # Update existing user to be the admin for this school
        admin_user.role = 'A'
        admin_user.school_id = school.id
        admin_user.is_active = True
        current_app.logger.info(f"Updated existing user {school.admin_email} to Admin for {school.name}")

    # Set/Update the password
    admin_user.set_password(new_password)
    
    # Activate the school
    school.is_active = True
    school.status = 'Active'
    school.last_payment_status = 'Confirmed'
    db.session.commit()
    
    # 2. Physical Database Separation
    db_name = f"`madrasah_tenant_{school.subdomain}`"
    try:
        # 1. Create the database
        from sqlalchemy import text
        db.session.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        db.session.commit()
        
        # 2. Initialize default permissions for the new school
        default_permissions = [
            ('T', 'attendance', True),
            ('T', 'classes', True),
            ('T', 'exams', True),
            ('T', 'students', True),
            ('S', 'students', True),
            ('S', 'teachers', True),
            ('S', 'financials', False),
            ('F', 'financials', True),
            ('P', 'financials', False),
        ]
        from app.models.permission import RolePermission
        for role, module, allowed in default_permissions:
            RolePermission.set_permission_for_school(role, module, allowed, school.id)

        # 3. Initialize default settings for the new school
        from app.models.setting import SystemSetting
        SystemSetting.set_setting('madrasah_name', school.name, school_id=school.id)
        SystemSetting.set_setting('active_term', 'First Term 2026', school_id=school.id)

        # 4. Run migrations/schema on the new database
        import subprocess
        import os
        
        # Get DB connection info from environment or config
        db_user = os.environ.get('DB_USER', 'madrasah_admin')
        db_pass = os.environ.get('DB_PASS', 'RaysTech2026')
        db_host = os.environ.get('DB_HOST', 'localhost')
        
        # Full paths to binaries to ensure they are found
        MYSQLDUMP = "/usr/bin/mysqldump"
        MYSQL = "/usr/bin/mysql"
        
        # Get schema from main db and apply to new db
        clean_db_name = f"madrasah_tenant_{school.subdomain}"
        cmd = f"{MYSQLDUMP} -u {db_user} -p'{db_pass}' -h {db_host} --no-data madrasah_db | {MYSQL} -u {db_user} -p'{db_pass}' -h {db_host} {clean_db_name}"
        subprocess.run(cmd, shell=True, check=True)
        
        # Drop FK constraints that reference central 'users' table 
        # (cross-db FKs cause IntegrityErrors since users live in madrasah_db, not tenant db)
        fk_cleanup_sql = (
            "SET FOREIGN_KEY_CHECKS=0; "
            f"ALTER TABLE `{clean_db_name}`.announcements DROP FOREIGN KEY IF EXISTS announcements_ibfk_1; "
            "SET FOREIGN_KEY_CHECKS=1;"
        )
        fk_cmd = f"{MYSQL} -u {db_user} -p'{db_pass}' -h {db_host} -e \"{fk_cleanup_sql}\""
        try:
            subprocess.run(fk_cmd, shell=True, check=False)
            current_app.logger.info(f"✅ Removed cross-DB FK constraints from {clean_db_name}")
        except Exception as fk_e:
            current_app.logger.warning(f"⚠️ Could not remove FK constraints (non-fatal): {fk_e}")
        
        current_app.logger.info(f"✅ Physical Database created: {clean_db_name}")


    except Exception as e:
        current_app.logger.error(f"❌ Failed to initialize separate database {db_name}: {e}")
        # Note: We don't fail the whole request, but log it.
        
    # Send activation email with credentials
    email_sent = EmailService.send_activation_email(
        recipient_email=school.admin_email,
        password=new_password,
        school_name=school.name
    )
    
    if email_sent:
        flash(f"✅ School '{school.name}' approved! Credentials sent to {school.admin_email}", "success")
    else:
        flash(f"⚠️ School '{school.name}' approved, but email failed to send. Password: {new_password}", "warning")
    
    return redirect(url_for('saas_admin.list_schools'))

@saas_admin_bp.route("/schools/toggle/<int:id>")
@login_required
@saas_super_admin_required
def toggle_school(id):
    school = School.query.get_or_404(id)
    school.is_active = not school.is_active
    school.status = 'Active' if school.is_active else 'Suspended'
    db.session.commit()
    status_text = "activated" if school.is_active else "deactivated"
    flash(f"School '{school.name}' has been {status_text}!", "success")
    return redirect(url_for('saas_admin.list_schools'))

@saas_admin_bp.route("/schools")
@login_required
@saas_super_admin_required
def list_schools():
    try:
        # Show all schools including soft-deleted ones for the master admin
        schools = School.query.order_by(School.created_at.desc()).all()
        return render_template("saas_admin/schools.html", schools=schools)
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error in list_schools: {e}")
        return f"<h1>Internal Error</h1><pre>{traceback.format_exc()}</pre>", 500

@saas_admin_bp.route("/schools/delete/<int:id>")
@login_required
@saas_super_admin_required
def delete_school(id):
    from datetime import datetime
    school = School.query.get_or_404(id)
    school.deleted_at = datetime.utcnow()
    school.is_active = False
    school.status = 'Deleted'
    db.session.commit()
    flash(f"School '{school.name}' has been soft-deleted. It will be kept for 2 years before permanent removal.", "warning")
    return redirect(url_for('saas_admin.list_schools'))

@saas_admin_bp.route("/schools/permanent_delete/<int:id>")
@login_required
@saas_super_admin_required
def permanent_delete_school(id):
    """Permanently remove a school and its data from the master database."""
    school = School.query.get_or_404(id)
    school_name = school.name
    sid = id
    from sqlalchemy import text
    try:
        # 1. Broad cleanup in Master DB (madrasah_db)
        db.session.execute(text("USE `madrasah_db`"))
        
        # We need to find all users of this school to clean their logs/otps
        u_res = db.session.execute(text("SELECT id FROM users WHERE school_id = :sid"), {"sid": sid}).fetchall()
        u_ids = [r[0] for r in u_res]
        
        if u_ids:
            # Clean OTPs and LoginLogs for these users using proper parameter binding
            u_ids_tuple = tuple(u_ids)
            db.session.execute(text("DELETE FROM otps WHERE user_id IN :uids"), {"uids": u_ids_tuple})
            db.session.execute(text("DELETE FROM login_logs WHERE user_id IN :uids"), {"uids": u_ids_tuple})
            db.session.execute(text("DELETE FROM users WHERE id IN :uids"), {"uids": u_ids_tuple})
        
        # Clean up all other tables that are linked to school_id
        db_tables = ["exam_results", "attendance", "exams", "fees", "expenses", "announcements", "students", "teachers", "class_sessions", "class_schedules", "subjects", "categories", "system_settings", "role_permissions"]
        for t in db_tables:
            db.session.execute(text(f"DELETE FROM {t} WHERE school_id = :sid"), {"sid": sid})
        
        # 2. Drop the tenant database
        db_name = f"`madrasah_tenant_{school.subdomain}`"
        db.session.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        
        # 3. Finally delete the school itself
        db.session.execute(text("DELETE FROM schools WHERE id = :sid"), {"sid": sid})
        
        db.session.commit()
        flash(f"✅ School '{school_name}' and all its data have been permanently wiped out.", "danger")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Failed to permanently delete school {id}: {e}")
        flash(f"❌ Error during permanent deletion: {str(e)[:200]}", "danger")

    return redirect(url_for('saas_admin.list_schools'))




@saas_admin_bp.route("/schools/restore/<int:id>")
@login_required
@saas_super_admin_required
def restore_school(id):
    school = School.query.get_or_404(id)
    school.deleted_at = None
    school.is_active = True
    school.status = 'Active'
    db.session.commit()
    flash(f"School '{school.name}' has been restored successfully!", "success")
    return redirect(url_for('saas_admin.list_schools'))
