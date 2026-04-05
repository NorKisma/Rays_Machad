# ======================================================
# IMPORTS
# ======================================================

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_babel import gettext as _

from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import (LoginForm, RegisterForm, EditUserForm, 
                                       ForgotPasswordForm, ResetPasswordForm, 
                                       ChangePasswordForm, VerifyOTPForm, 
                                       ResetPasswordWithOTPForm)
from app.models.user import User
from app.models.student import Student
from app.models.class_schedule import ClassSchedule
from app.models.otp import OTP
from flask_mail import Message
from app.extensions import db, login_manager, mail, limiter
from app.utils.decorators import admin_required, permission_required

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(_('Password Reset Request'),
                  recipients=[user.email])
    msg.body = f'''{_('To reset your password, visit the following link:')}
{url_for('auth.reset_password', token=token, _external=True)}

{_('If you did not make this request then simply ignore this email and no changes will be made.')}
'''
    mail.send(msg)

def send_otp_email(user, otp_code):
    """Send OTP code via email"""
    subject = _('Password Reset OTP')
    msg = Message(subject,
                  recipients=[user.email])
    
    # Text Version
    msg.body = f'''{_('Your password reset OTP code is:')} {otp_code}

{_('This code will expire in 10 minutes.')}

{_('If you did not make this request, please ignore this email.')}'''

    # HTML Version
    msg.html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; padding: 30px; border: 1px solid #e0e0e0; border-radius: 12px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 25px; border-bottom: 2px solid #f0f0f0; margin-bottom: 25px; }}
            .logo {{ font-size: 24px; font-weight: 700; color: #4F46E5; text-transform: uppercase; letter-spacing: 1px; }}
            .content {{ text-align: center; padding: 10px 0; }}
            .greeting {{ font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #1F2937; }}
            .message {{ margin-bottom: 25px; color: #4B5563; }}
            .otp-box {{ background-color: #EEF2FF; border: 2px dashed #4F46E5; color: #4F46E5; font-size: 36px; font-weight: 800; letter-spacing: 8px; padding: 20px 40px; border-radius: 12px; display: inline-block; margin: 10px 0 25px 0; }}
            .expiry {{ color: #EF4444; font-size: 14px; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 5px; }}
            .footer {{ margin-top: 35px; font-size: 12px; color: #9CA3AF; text-align: center; border-top: 1px solid #F3F4F6; padding-top: 20px; }}
        </style>
    </head>
    <body style="background-color: #F9FAFB;">
        <div class="container">
            <div class="header">
                <div class="logo">Madrasah Management</div>
            </div>
            <div class="content">
                <div class="greeting">{_('Assalamu Alaykum')} {user.name},</div>
                <div class="message">{_('You requested a password reset. Use the code below to verify your identity:')}</div>
                
                <div class="otp-box">{otp_code}</div>
                
                <div class="expiry">
                    <span>⏰</span> {_('This code will expire in 10 minutes.')}
                </div>
                
                <p style="margin-top: 30px; font-size: 14px; color: #6B7280;">{_('If you did not request this, please ignore this email. No changes will be made to your account.')}</p>
            </div>
            <div class="footer">
                <p>&copy; {datetime.utcnow().year} Madrasah Management System. {_('All rights reserved.')}</p>
                <p style="margin-top: 5px;">{_('This is an automated message, please do not reply.')}</p>
            </div>
        </div>
    </body>
    </html>
    '''
    mail.send(msg)

# ======================================================
# LOGIN MANAGER
# ======================================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ======================================================
# LOGIN
# ======================================================
@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent')

        from app.models.security import LoginLog
        from app.utils.tenant_context import get_current_school
        current_school = get_current_school()

        if user:
            if user.deleted_at:
                flash(_("This account has been removed."), "danger")
                return redirect(url_for("auth.login"))

            if not user.is_active:
                flash(_("Your account has been deactivated."), "warning")
                return redirect(url_for("auth.login"))

            if user.check_password(form.password.data):
                is_saas_admin = user.email == 'nor.jws@gmail.com'
                
                # SaaS Isolation logic
                if current_school:
                    # On a school subdomain: user must belong to this school (except super admin)
                    if not is_saas_admin and user.school_id != current_school.id:
                        flash(_("You do not have access to this school's portal."), "danger")
                        return redirect(url_for("auth.login"))
                else:
                    # On the Master Domain (no school context): Only Super Admin can log in
                    if not is_saas_admin:
                        flash(_("Please log in through your school's specific portal (e.g., myschool.raystechcenter.online)"), "warning")
                        return redirect(url_for("auth.login"))

                login_user(user, remember=form.remember.data)
                user.last_login_at = datetime.utcnow()
                user.last_login_ip = ip_address
                user.last_login_attempt = datetime.utcnow()
                user.login_status = 'Success'
                
                # Create Log
                log = LoginLog(
                    user_id=user.id, 
                    school_id=current_school.id if current_school else user.school_id,
                    email=email, 
                    ip_address=ip_address, 
                    user_agent=user_agent, 
                    status='Success'
                )
                db.session.add(log)
                db.session.commit()

                flash(_("Welcome back!"), "success")
                next_page = request.args.get("next")
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for("auth.dashboard")
                return redirect(next_page)
            else:
                user.last_login_attempt = datetime.utcnow()
                user.login_status = 'Failed'
                
                # Create Log
                log = LoginLog(
                    user_id=user.id, 
                    school_id=current_school.id if current_school else user.school_id,
                    email=email, 
                    ip_address=ip_address, 
                    user_agent=user_agent, 
                    status='Failed'
                )
                db.session.add(log)
                db.session.commit()
            flash(_("Invalid email or password."), "danger")
        else:
            # Log failed attempt for non-existent user
            log = LoginLog(
                user_id=None, 
                school_id=current_school.id if current_school else None,
                email=email, 
                ip_address=ip_address, 
                user_agent=user_agent, 
                status='Failed'
            )
            db.session.add(log)
            db.session.commit()
            flash(_("Invalid email or password."), "danger")


    return render_template("login.html", login_form=form)


# ======================================================
# LOGOUT
# ======================================================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(_("You have been logged out."), "info")
    return redirect(url_for("auth.login"))


# ======================================================
# DASHBOARD
# ======================================================
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    from sqlalchemy import func
    from app.models.student import Student
    from app.models.teacher import Teacher
    from app.models.class_schedule import ClassSchedule
    from app.models.setting import SystemSetting
    from app.models.exam import Exam, ExamResult
    from app.models.attendance import Attendance
    
    from app.utils.tenant_context import get_current_school
    school = get_current_school()
    school_id = school.id if school else None
    
    total_students = Student.query.filter_by(school_id=school_id).count() if school_id else Student.query.count()
    total_teachers = Teacher.query.filter_by(school_id=school_id).count() if school_id else Teacher.query.count()
    total_classes = ClassSchedule.query.filter_by(school_id=school_id).count() if school_id else ClassSchedule.query.count()
    
    active_term = SystemSetting.get_setting('active_term', 'First Term 2026')
    madrasah_name = school.name if school else SystemSetting.get_setting('madrasah_name', 'Darul Arqam Madrasah')
    
    # --- Auto Billing Feature (Admin Only) ---
    if current_user.role == 'A':
        current_month = datetime.utcnow().strftime('%Y-%m')
        last_billing = SystemSetting.get_setting('last_auto_billing_month', '')
        
        if last_billing != current_month:
            from app.blueprints.financials.routes import generate_fees_logic
            stats = generate_fees_logic()
            SystemSetting.set_setting('last_auto_billing_month', current_month, 'Last month fees were auto-generated')
            
            if stats['generated'] > 0:
                flash(_("<strong>Auto-Billing:</strong> Generated %(count)s tuition records for %(month)s.", 
                        count=stats['generated'], month=stats['month']), 'info')

    from app.models.announcement import Announcement
    
    # Fetch announcements based on role
    role_name = 'Everyone'
    if current_user.role == 'T': role_name = 'Teachers'
    elif current_user.role == 'U': role_name = 'Students'
    elif current_user.role == 'P': role_name = 'Parents'

    announcements = Announcement.query.filter(
        (Announcement.target_audience == 'All') | 
        (Announcement.target_audience == role_name),
        (Announcement.expires_at == None) | (Announcement.expires_at > datetime.utcnow())
    ).order_by(Announcement.created_at.desc()).limit(5).all()

    # --- New Dashboard Widgets Data ---
    
    # 1. Top Students (based on total marks obtained)
    top_students_query = db.session.query(
        Student, 
        func.sum(ExamResult.marks_obtained).label('total_score')
    ).join(ExamResult, Student.id == ExamResult.student_id)
    
    if school_id:
        top_students_query = top_students_query.filter(Student.school_id == school_id)
        
    top_students = top_students_query.group_by(Student.id)\
     .order_by(db.desc('total_score'))\
     .limit(5).all()

    # 2. Recent Exams
    recent_exams_query = Exam.query
    if school_id:
        recent_exams_query = recent_exams_query.filter_by(school_id=school_id)
    recent_exams = recent_exams_query.order_by(Exam.exam_date.desc()).limit(5).all()

    # 3. Teacher Workload (classes per teacher)
    teacher_workload_query = db.session.query(
        Teacher,
        func.count(ClassSchedule.id).label('class_count')
    ).join(ClassSchedule, Teacher.id == ClassSchedule.teacher_id)
    
    if school_id:
        teacher_workload_query = teacher_workload_query.filter(Teacher.school_id == school_id)
        
    teacher_workload = teacher_workload_query.group_by(Teacher.id)\
     .order_by(db.desc('class_count'))\
     .limit(5).all()

    # 4. Recent Attendance Updates
    recent_attendance_query = Attendance.query
    if school_id:
        recent_attendance_query = recent_attendance_query.filter_by(school_id=school_id)
    recent_attendance = recent_attendance_query.order_by(Attendance.created_at.desc()).limit(5).all()

    # Common data for templates
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'active_term': active_term,
        'madrasah_name': madrasah_name,
        'announcements': announcements,
        'top_students': top_students,
        'recent_exams': recent_exams,
        'teacher_workload': teacher_workload,
        'recent_attendance': recent_attendance,
        'db': db
    }

    # Role-based template selection
    if current_user.role == 'A':
        return render_template("dashboard.html", **context)
    elif current_user.role == 'T':
        # Dynamic stats for Teachers
        teacher = current_user.teacher_profile
        my_classes_count = 0
        my_students_count = 0
        
        if teacher:
            # Count classes assigned directly to this teacher
            my_classes = teacher.classes # Backref from ClassSchedule
            my_classes_count = len(my_classes)
            for cls in my_classes:
                my_students_count += len(cls.students)
                
        return render_template("teacher_dashboard.html", 
                               teacher=teacher, 
                               my_classes_count=my_classes_count,
                               my_students_count=my_students_count,
                               **context)
    elif current_user.role == 'S':
        return render_template("staff_dashboard.html", **context)
    elif current_user.role == 'P':
        # Dynamic stats for Parents
        children = current_user.children
        total_due = 0
        attendance_records = 0
        present_count = 0
        
        for student in children:
            # Calculate due fees for this child
            for fee in student.fees:
                if fee.status == 'Unpaid':
                    total_due += float(fee.amount)
            
            # Calculate attendance stats
            student_attendance = student.attendances.all()
            attendance_records += len(student_attendance)
            present_count += len([a for a in student_attendance if a.status == 'Present'])

        attendance_avg = (present_count / attendance_records * 100) if attendance_records > 0 else 0
        
        return render_template("parent_dashboard.html", 
                               children=children, 
                               total_due=total_due, 
                               attendance_avg=round(attendance_avg, 1),
                               **context)

    elif current_user.role == 'U':
        # Dynamic stats for Students
        student = current_user.student_profile
        attendance_pct = 0
        
        if student:
            # Calculate attendance stats
            student_attendance = student.attendances.all()
            attendance_records = len(student_attendance)
            present_count = len([a for a in student_attendance if a.status == 'Present'])
            attendance_pct = (present_count / attendance_records * 100) if attendance_records > 0 else 0
            
        return render_template("student_dashboard.html", 
                               student=student, 
                               attendance_pct=round(attendance_pct, 1),
                               **context)
    
    return render_template("dashboard.html", **context)

@auth_bp.route("/my-children")
@login_required
def my_children():
    if current_user.role != 'P':
        return redirect(url_for('auth.dashboard'))
    
    children = current_user.children
    return render_template("my_children.html", children=children)

@auth_bp.route("/my-payments")
@login_required
def my_payments():
    if current_user.role != 'P':
        return redirect(url_for('auth.dashboard'))
    
    children = current_user.children
    all_fees = []
    total_unpaid = 0
    
    for child in children:
        child_fees = child.fees.order_by(db.desc('due_date')).all()
        all_fees.extend(child_fees)
        for fee in child_fees:
            if fee.status != 'Paid':
                total_unpaid += float(fee.amount)
                
    # Sort all fees by due date descending
    all_fees.sort(key=lambda x: x.due_date, reverse=True)
    
    return render_template("my_payments.html", fees=all_fees, total_unpaid=total_unpaid)


# ======================================================
# REGISTER USER
# ======================================================
@auth_bp.route("/register", methods=["GET", "POST"])
@permission_required('manage_users')
def register():
    from app.utils.tenant_context import get_current_school
    current_school = get_current_school()
    
    is_first_user = User.query.count() == 0
    form = RegisterForm()

    if is_first_user:
        form.role.data = "A"

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        role = "A" if is_first_user else form.role.data
        
        # Automatically assign to current school (if in a school subdomain)
        school_id = current_school.id if current_school else None
        
        user = User(
            name=form.name.data,
            email=email,
            password_hash=generate_password_hash(form.password.data),
            role=role,
            school_id=school_id,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        if is_first_user:
            login_user(user)
            flash(_("System setup completed. Welcome Admin!"), "success")
            return redirect(url_for("auth.dashboard"))

        flash(_("User registered successfully"), "success")
        return redirect(url_for("auth.manage_users"))

    return render_template("user.html", register_form=form, is_first_user=is_first_user)


# ======================================================
# MANAGE USERS
 # ======================================================
@auth_bp.route("/users")
@permission_required('manage_users')
def manage_users():
    from app.utils.tenant_context import get_current_school
    current_school = get_current_school()
    
    if current_user.is_super_admin:
        # SaaS super admin sees all users
        users = User.query.order_by(User.name).all()
    elif current_school:
        # School admin sees only their school's users
        users = User.query.filter_by(school_id=current_school.id).order_by(User.name).all()
    else:
        users = []
    
    return render_template("manage_users.html", users=users)





# ======================================================
# TOGGLE USER STATUS (Activate / Deactivate / Soft Delete / Restore)
# ======================================================
@auth_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@permission_required('manage_users')
def toggle_user_status(user_id):

    if current_user.id == user_id and not current_user.is_super_admin:
        flash(_("You cannot modify your own status."), "danger")
        return redirect(url_for("auth.manage_users"))

    user = User.query.get_or_404(user_id)

    # Hardened Security Check
    if user.is_super_admin and not current_user.is_super_admin:
        flash(_("Primary admin account is protected."), "danger")
        return redirect(url_for("auth.manage_users"))

    if not current_user.is_super_admin:
        flash(_("Only the super admin can perform this action."), "danger")
        return redirect(url_for("auth.manage_users"))

    action = request.form.get("action", "").strip()  # 'activate', 'deactivate', 'delete', 'restore', 'perm_delete'
    from flask import current_app
    current_app.logger.info(f"User Action: UserID={user_id}, Action={action}, By={current_user.email}")

    try:
        if action == "activate":
            user.is_active = True
            flash(_("User %(name)s has been activated.", name=user.name), "success")

        elif action == "deactivate":
            user.is_active = False
            flash(_("User %(name)s has been deactivated.", name=user.name), "success")

        elif action == "delete":
            user.deleted_at = datetime.utcnow()
            flash(_("User %(name)s has been soft-deleted.", name=user.name), "success")

        elif action == "restore":
            user.deleted_at = None
            flash(_("User %(name)s has been restored.", name=user.name), "success")

        elif action == "perm_delete":
            name = user.name
            uid = user.id
            user_school_id = user.school_id
            from sqlalchemy import text
            
            # 1. Cleanup in Central DB
            try:
                db.session.execute(text("USE `madrasah_db`"))
                db.session.execute(text("DELETE FROM otps WHERE user_id = :uid"), {"uid": uid})
                db.session.execute(text("DELETE FROM login_logs WHERE user_id = :uid"), {"uid": uid})
                db.session.execute(text("UPDATE teachers SET user_id = NULL WHERE user_id = :uid"), {"uid": uid})
                db.session.execute(text("UPDATE students SET parent_id = NULL WHERE parent_id = :uid"), {"uid": uid})
                db.session.execute(text("UPDATE students SET student_user_id = NULL WHERE student_user_id = :uid"), {"uid": uid})
                db.session.execute(text("UPDATE announcements SET created_by_id = NULL WHERE created_by_id = :uid"), {"uid": uid})
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.warning(f"Main DB cleanup error for User {uid}: {e}")

            # 2. Cleanup in Tenant DB
            if user_school_id:
                from app.models.school import School
                target_school = School.query.get(user_school_id)
                if target_school:
                    tenant_db = f"`madrasah_tenant_{target_school.subdomain}`"
                    try:
                        db.session.execute(text(f"USE {tenant_db}"))
                        db.session.execute(text("UPDATE teachers SET user_id = NULL WHERE user_id = :uid"), {"uid": uid})
                        db.session.execute(text("UPDATE students SET parent_id = NULL WHERE parent_id = :uid"), {"uid": uid})
                        db.session.execute(text("UPDATE students SET student_user_id = NULL WHERE student_user_id = :uid"), {"uid": uid})
                        db.session.execute(text("UPDATE announcements SET created_by_id = NULL WHERE created_by_id = :uid"), {"uid": uid})
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        current_app.logger.warning(f"Tenant DB cleanup failed for {tenant_db}: {e}")

            # 3. Final Step: RAW DELETE
            try:
                db.session.execute(text("USE `madrasah_db`"))
                db.session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": uid})
                db.session.commit()
                flash(_("User %(name)s has been permanently deleted.", name=name), "warning")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Final User deletion failed for {uid}: {e}")
                flash(_("Error: Permanent deletion failed. Database reason: %(err)s", err=str(e)[:100]), "danger")
            
            return redirect(url_for("auth.manage_users"))

        else:
            flash(_("Invalid action: %(action)s", action=action), "danger")
            return redirect(url_for("auth.manage_users"))

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(_("Error: This user cannot be deleted. They might be linked to records in another school or system files."), "danger")
        from flask import current_app
        current_app.logger.error(f"Error in toggle_user_status: {e}")

    return redirect(url_for("auth.manage_users"))


@auth_bp.route("/users/perm-delete-all", methods=["POST"])
@admin_required
def perm_delete_all_users():
    if not current_user.is_super_admin:
        flash(_("Only the super admin can perform this action."), "danger")
        return redirect(url_for("auth.manage_users"))
    
    deleted_users = User.query.filter(User.deleted_at.isnot(None)).all()
    count = 0
    from sqlalchemy import text
    
    for u in deleted_users:
        if u.is_super_admin: continue
        uid = u.id
        user_school_id = u.school_id
        
        # Aggressive cleanup in Main DB
        try:
            db.session.execute(text("USE `madrasah_db`"))
            db.session.execute(text("DELETE FROM otps WHERE user_id = :uid"), {"uid": uid})
            db.session.execute(text("DELETE FROM login_logs WHERE user_id = :uid"), {"uid": uid})
            db.session.execute(text("UPDATE teachers SET user_id = NULL WHERE user_id = :uid"), {"uid": uid})
            db.session.execute(text("UPDATE students SET parent_id = NULL WHERE parent_id = :uid"), {"uid": uid})
            db.session.execute(text("UPDATE students SET student_user_id = NULL WHERE student_user_id = :uid"), {"uid": uid})
            db.session.execute(text("UPDATE announcements SET created_by_id = NULL WHERE created_by_id = :uid"), {"uid": uid})
            db.session.execute(text("UPDATE exams SET created_by_id = NULL WHERE created_by_id = :uid"), {"uid": uid})
            db.session.commit()
        except:
            db.session.rollback()

        # Cleanup in Tenant DB
        if user_school_id:
            from app.models.school import School
            target_school = School.query.get(user_school_id)
            if target_school:
                tenant_db = f"`madrasah_tenant_{target_school.subdomain}`"
                try:
                    db.session.execute(text(f"USE {tenant_db}"))
                    db.session.execute(text("UPDATE teachers SET user_id = NULL WHERE user_id = :uid"), {"uid": uid})
                    db.session.execute(text("UPDATE students SET parent_id = NULL WHERE parent_id = :uid"), {"uid": uid})
                    db.session.execute(text("UPDATE students SET student_user_id = NULL WHERE student_user_id = :uid"), {"uid": uid})
                    db.session.execute(text("UPDATE announcements SET created_by_id = NULL WHERE created_by_id = :uid"), {"uid": uid})
                    db.session.execute(text("UPDATE exams SET created_by_id = NULL WHERE created_by_id = :uid"), {"uid": uid})
                    db.session.commit()
                except:
                    db.session.rollback()
        
        # Final Delete: Use RAW SQL to bypass SQLAlchemy backref loading issues
        try:
            db.session.execute(text("USE `madrasah_db`"))
            db.session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": uid})
            db.session.commit()
            count += 1
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Bulk RAW delete failed for {uid}: {e}")

    flash(_("Successfully wiped %(count)d users forever.", count=count), "warning")
    return redirect(url_for("auth.manage_users"))


@auth_bp.route("/users/restore-all", methods=["POST"])
@permission_required('manage_users')
def restore_all_users():
    if not current_user.is_super_admin:
        flash(_("Only the super admin can perform this action."), "danger")
        return redirect(url_for("auth.manage_users"))

    deleted_users = User.query.filter(User.deleted_at.isnot(None)).all()
    if not deleted_users:
        flash(_("No deleted users found to restore."), "info")
        return redirect(url_for("auth.manage_users"))

    count = 0
    for user in deleted_users:
        user.deleted_at = None
        count += 1
    
    db.session.commit()
    flash(_("Successfully restored %(count)s users.", count=count), "success")
    return redirect(url_for("auth.manage_users"))



# Edit user
@auth_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@permission_required('manage_users')
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    # Hardened Security Check
    if user.is_super_admin and not current_user.is_super_admin:
        flash(_("Primary admin account is protected."), "danger")
        return redirect(url_for("auth.manage_users"))

    if not current_user.is_super_admin:
        flash(_("Only the super admin can perform this action."), "danger")
        return redirect(url_for("auth.manage_users"))

    form = EditUserForm(obj=user, original_email=user.email)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data.lower()
        user.role = form.role.data
        db.session.commit()
        flash(_("User updated successfully."), "success")
        return redirect(url_for("auth.manage_users"))

    return render_template("edit_user.html", user=user, form=form)

# ======================================================
# FORGOT PASSWORD
# ======================================================
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            from flask import current_app
            try:
                # Create OTP for user
                otp = OTP.create_otp(user.id, purpose='password_reset', expiry_minutes=10)
                
                # Send OTP via email
                send_otp_email(user, otp.code)
                
                # Store user email in session for OTP verification
                session['reset_email'] = user.email
                
                flash(_("An OTP code has been sent to your email address."), "success")
                return redirect(url_for('auth.verify_otp'))
            except Exception as e:
                # Log error and provide fallback for development
                print(f"FAILED TO SEND OTP EMAIL: {str(e)}")
                
                if current_app.debug:
                    # In debug mode, show the OTP directly
                    otp = OTP.create_otp(user.id, purpose='password_reset', expiry_minutes=10)
                    session['reset_email'] = user.email
                    flash(_("System: Email sending failed (Check .env). Since you are in Debug Mode, here is your OTP:"), "warning")
                    flash(f"OTP Code: {otp.code}", "warning")
                    return redirect(url_for('auth.verify_otp'))
                else:
                    flash(_("There was an error sending the email. Please contact support or check server logs."), "danger")
        else:
            flash(_("If that account exists, an OTP code has been sent."), "info")
            
    return render_template("forgot_password.html", form=form)


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    
    # Check if email is in session
    if 'reset_email' not in session:
        flash(_("Please request a password reset first."), "warning")
        return redirect(url_for('auth.forgot_password'))
    
    form = VerifyOTPForm()
    if form.validate_on_submit():
        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Verify OTP
            success, message = OTP.verify_otp(user.id, form.otp.data, purpose='password_reset')
            
            if success:
                # Store verified flag in session
                session['otp_verified'] = True
                session['verified_user_id'] = user.id
                flash(_("OTP verified successfully! Please enter your new password."), "success")
                return redirect(url_for('auth.reset_password_with_otp'))
            else:
                flash(_(message), "danger")
        else:
            flash(_("Invalid session. Please try again."), "danger")
            return redirect(url_for('auth.forgot_password'))
    
    return render_template("verify_otp.html", form=form, email=session.get('reset_email'))


@auth_bp.route("/reset-password-otp", methods=["GET", "POST"])
def reset_password_with_otp():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    
    # Check if OTP was verified
    if not session.get('otp_verified') or 'verified_user_id' not in session:
        flash(_("Please verify your OTP first."), "warning")
        return redirect(url_for('auth.verify_otp'))
    
    form = ResetPasswordWithOTPForm()
    if form.validate_on_submit():
        user = User.query.get(session['verified_user_id'])
        
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            
            # Clear session data
            session.pop('reset_email', None)
            session.pop('otp_verified', None)
            session.pop('verified_user_id', None)
            
            flash(_('Your password has been updated! You can now log in'), 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(_("Invalid session. Please try again."), "danger")
            return redirect(url_for('auth.forgot_password'))
    
    return render_template('reset_password_otp.html', form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
        
    user = User.verify_reset_token(token)
    if user is None:
        flash(_('That is an invalid or expired token'), 'danger')
        return redirect(url_for('auth.forgot_password'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been updated! You can now log in'), 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password.html', form=form)

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash(_("Your password has been updated!"), "success")
            return redirect(url_for('auth.dashboard'))
        else:
            flash(_("Current password is incorrect."), "danger")
            
    return render_template("change_password.html", form=form)

# ======================================================
# SYSTEM BACKUP
# ======================================================
@auth_bp.route("/backup")
@login_required
@admin_required
def trigger_backup():
    from app.utils.backup_manager import perform_system_backup, send_backup_to_email
    success, result = perform_system_backup()
    
    if success:
        backup_msg = _("<strong>Backup Successful!</strong> File saved locally.")
        
        # Try to send to email
        email_success, email_result = send_backup_to_email(result)
        if email_success:
            flash(f"{backup_msg} {_('Also sent to your Gmail/Email.')}", "success")
        else:
            flash(f"{backup_msg} <br> <small class='text-muted'>{_('Email failed: %(error)s', error=email_result)}</small>", "info")
    else:
        flash(_("<strong>Backup Failed!</strong> Error: %(error)s", error=result), "danger")
        
    return redirect(url_for('auth.dashboard'))

@auth_bp.route("/logs")
@login_required
@admin_required
def view_logs():
    from app.models.security import LoginLog
    from app.models.user import User
    from app.utils.tenant_context import get_current_school
    current_school = get_current_school()
    
    # Super Admin logic
    if current_user.is_super_admin:
        if current_school:
            # Super admin viewing a specific school's dashboard/logs on a subdomain
            logs = LoginLog.query.filter_by(school_id=current_school.id).order_by(LoginLog.timestamp.desc()).limit(500).all()
        else:
            # Super admin on master domain - see everything
            logs = LoginLog.query.order_by(LoginLog.timestamp.desc()).limit(500).all()
    else:
        # Regular School Admin isolation
        # They should only see logs for their school (ID matches) or their users.
        school_id = current_user.school_id
        logs = LoginLog.query.outerjoin(User, LoginLog.user_id == User.id)\
               .filter((LoginLog.school_id == school_id) | (User.school_id == school_id))\
               .order_by(LoginLog.timestamp.desc()).limit(500).all()
        
    return render_template("login_logs.html", logs=logs)

@auth_bp.route("/restore", methods=["POST"])
@login_required
@admin_required
def restore_backup():
    if 'backup_file' not in request.files:
        flash(_("No file part"), "danger")
        return redirect(url_for('auth.dashboard'))
    
    file = request.files['backup_file']
    if file.filename == '':
        flash(_("No selected file"), "danger")
        return redirect(url_for('auth.dashboard'))
    
    if file:
        import tempfile
        from app.utils.backup_manager import restore_database_from_file
        
        # Save to a temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        success, message = restore_database_from_file(temp_path)
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if success:
            flash(_("<strong>Restore Successful!</strong> System data has been updated."), "success")
        else:
            flash(_("<strong>Restore Failed!</strong> Error: %(error)s", error=message), "danger")
            
    return redirect(url_for('auth.dashboard'))