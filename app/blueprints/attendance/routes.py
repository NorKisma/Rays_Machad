from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.attendance import attendance_bp
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.class_schedule import ClassSchedule
from app.extensions import db
from datetime import date, datetime
from flask_babel import _

from app.utils.decorators import admin_required, staff_required, teacher_required
from flask import abort
from app.models.subject import Subject

@attendance_bp.route("/")
@teacher_required
def index():
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    # Get all available classes for the dropdown
    all_classes_query = ClassSchedule.query
    if current_user.role == 'T' and current_user.teacher_profile:
        all_classes_query = all_classes_query.filter_by(teacher_id=current_user.teacher_profile.id)
    elif current_user.role == 'T':
        all_classes_query = None
    
    all_classes = all_classes_query.all() if all_classes_query else []
    
    # Filter classes for the cards/view based on selection
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    period = request.args.get('period', type=int, default=1)
    
    filter_classes = all_classes
    if class_id:
        filter_classes = [c for c in filter_classes if c.id == class_id]
    if subject_id and subject_id != 0:
        filter_classes = [c for c in filter_classes if c.subject_id == subject_id]
        
    subjects = Subject.query.order_by(Subject.name).all()
    if class_id:
        selected_class = ClassSchedule.query.get(class_id)
        if selected_class and selected_class.subject_id:
            subjects = [s for s in subjects if s.id == selected_class.subject_id]
            # Automatically set subject_id if not selected but class is
            if not subject_id:
                subject_id = selected_class.subject_id
        
    return render_template("attendance/index.html", 
                           all_classes=all_classes,
                           classes=filter_classes, 
                           subjects=subjects, 
                           selected_date=selected_date,
                           period=period,
                           selected_class_id=class_id,
                           selected_subject_id=subject_id)

@attendance_bp.route("/mark/<int:class_id>", methods=["GET", "POST"])
@teacher_required
def mark_attendance(class_id):
    cls = ClassSchedule.query.get_or_404(class_id)
    
    # Permission Check: Teacher can only mark attendance for their own class
    if current_user.role == 'T':
        if not current_user.teacher_profile or cls.teacher_id != current_user.teacher_profile.id:
            abort(403)
            
    selected_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    subject_id = request.args.get('subject_id', type=int)
    subject_id = subject_id if subject_id != 0 else None
    period = request.args.get('period', type=int, default=1)
    
    students = Student.query.filter_by(class_id=class_id, status='Active').all()
    
    # Check if attendance already exists for this day/class/subject/period
    existing_attendance = Attendance.query.filter_by(
        class_id=class_id, 
        attendance_date=selected_date, 
        subject_id=subject_id,
        period=period
    ).all()
    attendance_map = {a.student_id: a.status for a in existing_attendance}
    
    if request.method == "POST":
        # Delete existing for this date/class/subject/period to overwrite
        Attendance.query.filter_by(
            class_id=class_id, 
            attendance_date=selected_date, 
            subject_id=subject_id,
            period=period
        ).delete()
        
        for student in students:
            status = request.form.get(f"status_{student.id}", "Absent")
            remarks = request.form.get(f"remarks_{student.id}", "")
            
            # Use the teacher assigned to the class
            teacher_id = cls.teacher_id 
            
            new_record = Attendance(
                student_id=student.id,
                teacher_id=teacher_id,
                class_id=class_id,
                subject_id=subject_id,
                period=period,
                attendance_date=selected_date,
                status=status,
                remarks=remarks
            )
            db.session.add(new_record)
            
        db.session.commit()
        flash(_('Attendance marked successfully!'), 'success')
        return redirect(url_for('attendance.index', date=selected_date_str, subject_id=request.args.get('subject_id', 0), period=period))

    subject = Subject.query.get(subject_id) if subject_id else None

    return render_template("attendance/mark.html", 
                           cls=cls, 
                           students=students, 
                           selected_date=selected_date_str,
                           attendance_map=attendance_map,
                           subject=subject,
                           period=period)
@attendance_bp.route("/history")
@login_required
def history():
    """View detailed attendance history with filters"""
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    period = request.args.get('period', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    query = Attendance.query
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if period:
        query = query.filter_by(period=period)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query = query.filter(Attendance.attendance_date >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        query = query.filter(Attendance.attendance_date <= end_date)
    
    # Permission Check: Teacher can only see their own classes
    if current_user.role == 'T' and current_user.teacher_profile:
        my_class_ids = [c.id for c in ClassSchedule.query.filter_by(teacher_id=current_user.teacher_profile.id).all()]
        query = query.filter(Attendance.class_id.in_(my_class_ids))
    
    attendance_records = query.order_by(Attendance.attendance_date.desc(), Attendance.period.desc()).limit(500).all()
    
    classes = ClassSchedule.query.all()
    subjects = Subject.query.all()
    
    return render_template("attendance/history.html", 
                           attendance_records=attendance_records,
                           classes=classes,
                           subjects=subjects)
