from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app.blueprints.students import students_bp
from .forms import StudentRegistrationForm
from app.models.student import Student
from app.models.class_schedule import ClassSchedule # Assuming this holds class names
from app.models.user import User
from app.extensions import db
from flask_babel import _

from app.utils.decorators import admin_required, permission_required
from app.utils.generators import generate_student_id

@students_bp.route('/manage')
@permission_required('students')
def manage_students():
    class_id = request.args.get('class_id', type=int)
    search_query = request.args.get('search')
    
    query = Student.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    if search_query:
        query = query.filter(
            (Student.full_name.ilike(f'%{search_query}%')) |
            (Student.enrollment_number.ilike(f'%{search_query}%'))
        )
            
    # Filter by teacher if applicable
    if current_user.role == 'T' and current_user.teacher_profile:
        my_class_ids = [c.id for c in current_user.teacher_profile.classes]
        query = query.filter(Student.class_id.in_(my_class_ids))
    
    students = [] # Initialize students list
    
    if current_user.role == 'T':
        if current_user.teacher_profile:
            my_class_ids = [c.id for c in current_user.teacher_profile.classes]
            query = query.filter(Student.class_id.in_(my_class_ids))
            students = query.all()
        else:
            # Teacher has no profile, so no students are associated
            students = [] 
    else:
        # Admin or Staff can see all students (after initial filters)
        students = query.all()
        
    selected_class = ClassSchedule.query.get(class_id) if class_id else None
    
    # Status counts for the summary cards
    active_count = len([s for s in students if s.status == 'Active'])
    pending_count = len([s for s in students if s.status == 'Pending'])
    inactive_count = len([s for s in students if s.status == 'Inactive'])
        
    return render_template('students/manage_students.html', 
                           students=students, 
                           selected_class=selected_class,
                           active_count=active_count,
                           pending_count=pending_count,
                           inactive_count=inactive_count)

@students_bp.route('/add', methods=['GET', 'POST'])
@permission_required('students')
def add_student():
    form = StudentRegistrationForm()
    
    # Dynamically load classes, parents, and student accounts
    classes = ClassSchedule.query.all()
    form.student_class.choices = [(c.id, c.class_name) for c in classes]
    
    parents = User.query.filter_by(role='P').all()
    form.linked_parent.choices = [(0, _('None'))] + [(u.id, f"{u.name} ({u.email})") for u in parents]
    
    student_users = User.query.filter_by(role='U').all()
    form.student_user.choices = [(0, _('None'))] + [(u.id, f"{u.name} ({u.email})") for u in student_users]
    
    # Auto-generate next enrollment number suggestion
    if request.method == 'GET' and not form.enrollment_number.data:
        form.enrollment_number.data = generate_student_id()

    if form.validate_on_submit():
        new_student = Student(
            full_name=form.full_name.data,
            enrollment_number=form.enrollment_number.data,
            class_id=form.student_class.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            father_name=form.father_name.data,
            mother_name=form.mother_name.data,
            parent_contact=form.parent_contact.data,
            address=form.address.data,
            hifz_status=form.hifz_status.data,
            current_juz=form.current_juz.data,
            current_surah=form.current_surah.data,
            current_aya=form.current_aya.data,
            monthly_fee=form.monthly_fee.data,
            status=form.status.data,
            parent_id=form.linked_parent.data if form.linked_parent.data != 0 else None,
            student_user_id=form.student_user.data if form.student_user.data != 0 else None
        )
        db.session.add(new_student)
        db.session.commit()
        
        flash(_("Student %(name)s registered successfully!", name=form.full_name.data), 'success')
        return redirect(url_for('students.manage_students'))
    
    return render_template('students/add_student.html', form=form)

@students_bp.route('/profile/<int:student_id>')
@login_required
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Permission Check
    is_authorized = False
    
    if current_user.role in ['A', 'S']:
        is_authorized = True
    elif current_user.role == 'T' and current_user.teacher_profile:
        # Check if teacher handles this student's class
        my_class_ids = [c.id for c in current_user.teacher_profile.classes]
        if student.class_id in my_class_ids:
            is_authorized = True
    elif current_user.role == 'P':
        # Check if parent of this student
        if student.parent_id == current_user.id:
            is_authorized = True
    elif current_user.role == 'U' and current_user.student_profile:
        # Check if viewing own profile
        if current_user.student_profile.id == student.id:
            is_authorized = True
            
    if not is_authorized:
        abort(403)
    # Fetch history
    attendance_history = student.attendances.order_by(db.desc('attendance_date')).limit(30).all()
    exam_results = student.exam_results.order_by(db.desc('id')).all()
    
    # Quran Progress
    from app.models.quran import QuranProgress, QuranSession
    quran_progress = QuranProgress.query.filter_by(student_id=student.id).first()
    quran_sessions = []
    if quran_progress:
        quran_sessions = QuranSession.query.filter_by(progress_id=quran_progress.id).order_by(db.desc('session_date')).limit(15).all()

    # Only fetch fees if NOT a teacher
    fees = []
    if current_user.role != 'T':
        fees = student.fees.order_by(db.desc('due_date')).all()

    # Prepare attendance chart data (Present, Absent, Late)
    from app.models.attendance import Attendance
    present_count = student.attendances.filter_by(status='Present').count()
    absent_count = student.attendances.filter_by(status='Absent').count()
    late_count = student.attendances.filter_by(status='Late').count()
    
    attendance_stats = [present_count, absent_count, late_count]
    attendance_labels = [_('Present'), _('Absent'), _('Late')]

    return render_template('students/view_profile.html', 
                           student=student, 
                           attendance_history=attendance_history,
                           exam_results=exam_results,
                           fees=fees,
                           attendance_stats=attendance_stats,
                           attendance_labels=attendance_labels,
                           quran_progress=quran_progress,
                           quran_sessions=quran_sessions)

@students_bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@permission_required('students')
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentRegistrationForm(obj=student, original_enrollment=student.enrollment_number)
    
    # Pre-select the current class and parent
    classes = ClassSchedule.query.all()
    form.student_class.choices = [(c.id, c.class_name) for c in classes]
    
    parents = User.query.filter_by(role='P').all()
    form.linked_parent.choices = [(0, _('None'))] + [(u.id, f"{u.name} ({u.email})") for u in parents]
    
    student_users = User.query.filter_by(role='U').all()
    form.student_user.choices = [(0, _('None'))] + [(u.id, f"{u.name} ({u.email})") for u in student_users]
    
    if request.method == 'GET':
        form.student_class.data = student.class_id
        form.linked_parent.data = student.parent_id or 0
        form.student_user.data = student.student_user_id or 0

    if form.validate_on_submit():
        student.full_name = form.full_name.data
        student.enrollment_number = form.enrollment_number.data
        student.class_id = form.student_class.data
        student.date_of_birth = form.date_of_birth.data
        student.gender = form.gender.data
        student.father_name = form.father_name.data
        student.mother_name = form.mother_name.data
        student.parent_contact = form.parent_contact.data
        student.address = form.address.data
        student.hifz_status = form.hifz_status.data
        student.current_juz = form.current_juz.data
        student.current_surah = form.current_surah.data
        student.current_aya = form.current_aya.data
        student.monthly_fee = form.monthly_fee.data
        student.status = form.status.data
        student.parent_id = form.linked_parent.data if form.linked_parent.data != 0 else None
        student.student_user_id = form.student_user.data if form.student_user.data != 0 else None
        
        db.session.commit()
        flash(_("Student %(name)s updated successfully!", name=student.full_name), 'success')
        return redirect(url_for('students.manage_students'))
        
    return render_template('students/add_student.html', form=form, is_edit=True, student=student)

@students_bp.route('/delete/<int:student_id>', methods=['POST'])
@permission_required('students')
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.full_name
    db.session.delete(student)
    db.session.commit()
    flash(_("Student %(name)s deleted successfully!", name=name), 'warning')
    return redirect(url_for('students.manage_students'))

@students_bp.route('/id-card/<int:student_id>')
@permission_required('students')
def view_id_card(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('students/id_card.html', student=student)
@students_bp.route('/send-whatsapp/<int:student_id>', methods=['POST'])
@permission_required('students')
def send_whatsapp(student_id):
    student = Student.query.get_or_404(student_id)
    if not student.parent_contact:
        flash(_("Parent contact is missing for this student."), 'danger')
        return redirect(url_for('students.student_profile', student_id=student.id))
    
    from app.utils.messaging import MessagingService
    from app.ai_automation.notification_bot import NotificationBot
    from flask import session
    
    bot = NotificationBot()
    messenger = MessagingService()
    
    lang = session.get('lang') or request.accept_languages.best_match(['en', 'so', 'ar']) or 'en'
    
    # Generate a simple progress update message
    parent_name = student.father_name or student.mother_name or _("Parent")
    message = bot.generate_progress_update(
        parent_name, 
        student.full_name, 
        student.current_juz or 1, 
        student.current_surah or 'N/A', 
        student.current_aya or '0',
        lang=lang
    )
    
    success, info = messenger.send_hybrid_message(student.parent_contact, message)
    if success:
        flash(_("Progress update sent to parent successfully!"), 'success')
    else:
        flash(_("Failed to send message: %(error)s", error=str(info)), 'danger')
        
    return redirect(url_for('students.student_profile', student_id=student.id))

@students_bp.route('/print-all')
@permission_required('students')
def print_all_students():
    students = Student.query.order_by(Student.full_name).all()
    return render_template('students/print_directory.html', students=students)
