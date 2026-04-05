from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.teachers import teachers_bp
from app.models.teacher import Teacher
from .forms import TeacherRegistrationForm
from app.extensions import db
from flask_babel import _

from app.utils.decorators import admin_required, staff_required, teacher_required, permission_required
from flask import abort

@teachers_bp.route("/")
@permission_required('teachers')
def manage_teachers():
    teachers = Teacher.query.all()
    return render_template("teachers/manage_teachers.html", teachers=teachers)

@teachers_bp.route("/add", methods=["GET", "POST"])
@permission_required('teachers')
def add_teacher():
    form = TeacherRegistrationForm()
    
    # Auto-generate employee number suggestion
    if request.method == 'GET' and not form.employee_number.data:
        from app.utils.generators import generate_teacher_id
        form.employee_number.data = generate_teacher_id()
        
    from app.models.user import User
    teacher_users = User.query.filter_by(role='T').all()
    form.linked_user.choices = [(0, _('None'))] + [(u.id, f"{u.name} ({u.email})") for u in teacher_users]
    
    if form.validate_on_submit():
        teacher = Teacher(
            full_name=form.full_name.data,
            employee_number=form.employee_number.data,
            email=form.email.data,
            phone=form.phone.data,
            specialization=form.specialization.data,
            qualification=form.qualification.data,
            monthly_salary=form.monthly_salary.data or 0,
            joining_date=form.joining_date.data,
            status=form.status.data,
            user_id=form.linked_user.data if form.linked_user.data != 0 else None
        )
        db.session.add(teacher)
        try:
            db.session.commit()
            flash(_("Teacher registered successfully!"), "success")
            return redirect(url_for("teachers.manage_teachers"))
        except Exception as e:
            db.session.rollback()
            flash(_("Error: Employee ID or Email already exists."), "danger")
            
    return render_template("teachers/add_teacher.html", form=form)

@teachers_bp.route("/edit/<int:teacher_id>", methods=["GET", "POST"])
@permission_required('teachers')
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherRegistrationForm(obj=teacher)
    
    from app.models.user import User
    teacher_users = User.query.filter_by(role='T').all()
    form.linked_user.choices = [(0, _('None'))] + [(u.id, f"{u.name} ({u.email})") for u in teacher_users]
    
    if request.method == 'GET':
        form.linked_user.data = teacher.user_id or 0
        
    if form.validate_on_submit():
        teacher.full_name = form.full_name.data
        teacher.employee_number = form.employee_number.data
        teacher.email = form.email.data
        teacher.phone = form.phone.data
        teacher.specialization = form.specialization.data
        teacher.qualification = form.qualification.data
        teacher.monthly_salary = form.monthly_salary.data or 0
        teacher.joining_date = form.joining_date.data
        teacher.status = form.status.data
        teacher.user_id = form.linked_user.data if form.linked_user.data != 0 else None
        
        try:
            db.session.commit()
            flash(_("Teacher updated successfully!"), "success")
            return redirect(url_for("teachers.manage_teachers"))
        except Exception as e:
            db.session.rollback()
            flash(_("Error updating teacher. Details might already exist."), "danger")
            
    return render_template("teachers/add_teacher.html", form=form, is_edit=True, teacher=teacher)

@teachers_bp.route("/schedule/<int:teacher_id>")
@teacher_required
def view_schedule(teacher_id):
    from app.models.session import ClassSession
    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Permission check: Teacher can only view their own schedule
    if current_user.role == 'T' and (not current_user.teacher_profile or current_user.teacher_profile.id != teacher_id):
        abort(403)
    
    # Get all class IDs this teacher handles
    class_ids = [c.id for c in teacher.classes]
    
    # Fetch all sessions for these classes
    sessions = []
    if class_ids:
        sessions = ClassSession.query.filter(ClassSession.class_id.in_(class_ids)).all()
        
    return render_template("teachers/view_schedule.html", teacher=teacher, sessions=sessions)

@teachers_bp.route("/profile/<int:teacher_id>")
@teacher_required
def teacher_profile(teacher_id):
    from app.models.fee import Expense
    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Permission check: Teacher can only view their own profile (or admin/staff)
    if current_user.role == 'T' and (not current_user.teacher_profile or current_user.teacher_profile.id != teacher_id):
        abort(403)
        
    payouts = teacher.expenses.order_by(Expense.expense_date.desc()).all()
    return render_template("teachers/view_profile.html", teacher=teacher, payouts=payouts)

@teachers_bp.route("/print-all")
@permission_required('teachers')
def print_all_teachers():
    teachers = Teacher.query.order_by(Teacher.full_name).all()
    return render_template("teachers/print_directory.html", teachers=teachers)
