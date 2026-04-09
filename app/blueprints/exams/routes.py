# app/blueprints/exams/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from datetime import datetime

from app.blueprints.exams import exams_bp
from app.blueprints.exams.forms import ExamForm, ExamResultForm
from app.models.exam import Exam, ExamResult
from app.models.teacher import Teacher
from app.models.class_schedule import ClassSchedule
from app.models.category import Category
from app.models.subject import Subject
from app.models.student import Student
from app.extensions import db
from app.utils.decorators import admin_required, staff_required, teacher_required
from flask import abort

@exams_bp.route('/')
@teacher_required
def manage_exams():
    """View all exams with filtering"""
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    
    query = Exam.query
    
    if current_user.role == 'T' and current_user.teacher_profile:
        query = query.filter_by(teacher_id=current_user.teacher_profile.id)
    elif current_user.role == 'T':
        return render_template('exams/manage_exams.html', exams=[], subjects=[], classes=[])
        
    if class_id:
        query = query.filter_by(class_id=class_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
        
    exams = query.order_by(Exam.exam_date.desc()).all()
    
    # Group exams by name, type, month-year, and class
    from collections import OrderedDict
    grouped_exams_dict = OrderedDict()
    
    for exam in exams:
        class_id_str = str(exam.class_id) if exam.class_id else "none"
        group_key = f"{exam.exam_name.lower().strip()}_{exam.exam_type}_{exam.exam_date.strftime('%Y-%m')}_{class_id_str}"
        
        if group_key not in grouped_exams_dict:
            grouped_exams_dict[group_key] = {
                'exam_name': exam.exam_name,
                'exam_type': exam.exam_type,
                'exam_date': exam.exam_date,
                'teacher': exam.teacher,
                'class_assigned': exam.class_assigned,
                'status': exam.status,
                'sub_exams': [],
                'student_ids': set()
            }
        
        group = grouped_exams_dict[group_key]
        group['sub_exams'].append(exam)
        # Count unique students who have results with marks
        for result in exam.results:
            if result.marks_obtained is not None:
                group['student_ids'].add(result.student_id)
                
    grouped_exams = list(grouped_exams_dict.values())
    
    subjects = Subject.query.order_by(Subject.name).all()
    classes = ClassSchedule.query.order_by(ClassSchedule.class_name).all()
    
    return render_template('exams/manage_exams.html', 
                           grouped_exams=grouped_exams, 
                           subjects=subjects, 
                           classes=classes)


@exams_bp.route('/add', methods=['GET', 'POST'])
@teacher_required
def add_exam():
    """Create a new exam"""
    form = ExamForm()
    
    # Standard Exam Types (Fixed)
    form.exam_type.choices = [
        ('Hifz', _('Hifz Oral')), 
        ('Tajweed', _('Tajweed Practice')),
        ('Written', _('Written Exam')),
        ('Oral', _('Oral Exam')),
        ('Practical', _('Practical/Activity')),
        ('Midterm', _('Midterm Exam')),
        ('Final', _('Final Exam')),
        ('Quiz', _('Quiz/Test'))
    ]
    
    # Populate dropdowns
    subjects = Subject.query.order_by(Subject.category, Subject.name).all()
    form.subject_id.choices = [(0, _('No Specific Subject'))] + [(s.id, f"{s.name} ({s.category or 'General'})") for s in subjects]
    
    if current_user.role == 'T' and current_user.teacher_profile:
        my_classes = ClassSchedule.query.filter_by(teacher_id=current_user.teacher_profile.id).all()
        form.class_id.choices = [(0, _('All My Classes'))] + [(c.id, c.class_name) for c in my_classes]
        form.teacher_id.choices = [(current_user.teacher_profile.id, current_user.teacher_profile.full_name)]
        form.teacher_id.data = current_user.teacher_profile.id
    else:
        form.class_id.choices = [(0, _('All Classes'))] + [(c.id, c.class_name) for c in ClassSchedule.query.order_by(ClassSchedule.class_name).all()]
        form.teacher_id.choices = [(t.id, t.full_name) for t in Teacher.query.order_by(Teacher.full_name).all()]
    
    if form.validate_on_submit():
        exam = Exam(
            exam_name=form.exam_name.data,
            exam_type=form.exam_type.data,
            class_id=form.class_id.data if form.class_id.data != 0 else None,
            subject_id=form.subject_id.data if form.subject_id.data != 0 else None,
            teacher_id=form.teacher_id.data,
            exam_date=form.exam_date.data,
            total_marks=form.total_marks.data,
            passing_marks=form.passing_marks.data,
            surah_from=form.surah_from.data,
            surah_to=form.surah_to.data,
            juz_number=form.juz_number.data,
            description=form.description.data,
            status=form.status.data
        )
        db.session.add(exam)
        db.session.commit()
        
        flash(_('Exam "%(name)s" created successfully!', name=exam.exam_name), 'success')
        return redirect(url_for('exams.manage_exams'))
    
    return render_template('exams/add_exam.html', form=form)


@exams_bp.route('/edit/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def edit_exam(exam_id):
    """Edit an existing exam"""
    exam = Exam.query.get_or_404(exam_id)
    form = ExamForm(obj=exam)
    
    # Standard Exam Types (Fixed)
    form.exam_type.choices = [
        ('Hifz', _('Hifz Oral')), 
        ('Tajweed', _('Tajweed Practice')),
        ('Written', _('Written Exam')),
        ('Oral', _('Oral Exam')),
        ('Practical', _('Practical/Activity')),
        ('Midterm', _('Midterm Exam')),
        ('Final', _('Final Exam')),
        ('Quiz', _('Quiz/Test'))
    ]
    
    # Populate dropdowns
    subjects = Subject.query.order_by(Subject.category, Subject.name).all()
    form.subject_id.choices = [(0, _('No Specific Subject'))] + [(s.id, f"{s.name} ({s.category or 'General'})") for s in subjects]
    
    form.class_id.choices = [(0, _('All Classes'))] + [(c.id, c.class_name) for c in ClassSchedule.query.order_by(ClassSchedule.class_name).all()]
    form.teacher_id.choices = [(t.id, t.full_name) for t in Teacher.query.order_by(Teacher.full_name).all()]
    
    if request.method == 'GET':
        form.class_id.data = exam.class_id if exam.class_id else 0
        form.subject_id.data = exam.subject_id if exam.subject_id else 0
    
    if form.validate_on_submit():
        exam.exam_name = form.exam_name.data
        exam.exam_type = form.exam_type.data
        exam.class_id = form.class_id.data if form.class_id.data != 0 else None
        exam.subject_id = form.subject_id.data if form.subject_id.data != 0 else None
        exam.teacher_id = form.teacher_id.data
        exam.exam_date = form.exam_date.data
        exam.total_marks = form.total_marks.data
        exam.passing_marks = form.passing_marks.data
        exam.surah_from = form.surah_from.data
        exam.surah_to = form.surah_to.data
        exam.juz_number = form.juz_number.data
        exam.description = form.description.data
        exam.status = form.status.data
        
        db.session.commit()
        flash(_('Exam updated successfully!'), 'success')
        return redirect(url_for('exams.manage_exams'))
    
    return render_template('exams/add_exam.html', form=form, is_edit=True, exam=exam)


@exams_bp.route('/results/<int:exam_id>')
@teacher_required
def view_results(exam_id):
    """View results for a specific exam"""
    exam = Exam.query.get_or_404(exam_id)
    
    # Permission Check
    if current_user.role == 'T':
        if not current_user.teacher_profile or exam.teacher_id != current_user.teacher_profile.id:
            abort(403)
    
    # Get all students for this exam
    if exam.class_id:
        students = Student.query.filter_by(class_id=exam.class_id).all()
    else:
        students = Student.query.all()
    
    # Get existing results
    results = {r.student_id: r for r in exam.results}
    
    return render_template('exams/view_results.html', exam=exam, students=students, results=results)


@exams_bp.route('/enter-result/<int:exam_id>/<int:student_id>', methods=['GET', 'POST'])
@teacher_required
def enter_result(exam_id, student_id):
    """Enter or edit result for a student"""
    exam = Exam.query.get_or_404(exam_id)
    
    # Permission Check
    if current_user.role == 'T':
        if not current_user.teacher_profile or exam.teacher_id != current_user.teacher_profile.id:
            abort(403)
    student = Student.query.get_or_404(student_id)
    
    # Check if result already exists
    result = ExamResult.query.filter_by(exam_id=exam_id, student_id=student_id).first()
    
    form = ExamResultForm(obj=result)
    
    if form.validate_on_submit():
        if not result:
            result = ExamResult(exam_id=exam_id, student_id=student_id)
            db.session.add(result)
        
        result.marks_obtained = form.marks_obtained.data
        result.memorization_accuracy = form.memorization_accuracy.data
        result.tajweed_score = form.tajweed_score.data
        result.fluency_score = form.fluency_score.data
        result.status = form.status.data
        result.remarks = form.remarks.data
        # Find the teacher associated with the current user, if any
        evaluator = Teacher.query.filter_by(email=current_user.email).first()
        result.evaluated_by = evaluator.id if evaluator else None
        result.evaluated_at = datetime.utcnow()
        
        # Calculate grade
        if result.marks_obtained is not None:
            result.grade = result.calculate_grade(exam.total_marks)
        
        db.session.commit()
        flash(_('Result saved for %(student)s', student=student.full_name), 'success')
        return redirect(url_for('exams.view_results', exam_id=exam_id))
    
    return render_template('exams/enter_result.html', form=form, exam=exam, student=student, result=result)


@exams_bp.route('/delete/<int:exam_id>', methods=['POST'])
@staff_required
def delete_exam(exam_id):
    """Delete an exam"""
    exam = Exam.query.get_or_404(exam_id)
    exam_name = exam.exam_name
    db.session.delete(exam)
    db.session.commit()
    flash(_('Exam "%(name)s" deleted successfully!', name=exam_name), 'warning')
    return redirect(url_for('exams.manage_exams'))


@exams_bp.route('/student-report/<int:student_id>')
@login_required
def student_report(student_id):
    """View all exam results for a specific student"""
    student = Student.query.get_or_404(student_id)
    results = ExamResult.query.filter_by(student_id=student_id).join(Exam).order_by(Exam.exam_date.desc()).all()
    
    return render_template('exams/student_report.html', student=student, results=results)


@exams_bp.route('/rankings')
@login_required
def student_rankings():
    """Overall Student Rankings based on their exam results"""
    from app.models.student import Student
    
    # Get all active students
    students = Student.query.filter_by(status='Active').all()
    rankings = []
    
    for student in students:
        results = [r for r in student.exam_results if r.marks_obtained is not None and r.exam.total_marks]
        
        if not results:
            continue
            
        total_obtained = sum(r.marks_obtained for r in results)
        total_max = sum(r.exam.total_marks for r in results)
        
        if total_max > 0:
            percentage = (total_obtained / total_max) * 100
        else:
            percentage = 0
            
        # Fetch grading thresholds from settings (default values if not set)
        from app.models.setting import SystemSetting
        grade_a_plus = int(SystemSetting.get_setting('grade_a_plus', '90'))
        grade_a = int(SystemSetting.get_setting('grade_a', '80'))
        grade_b_plus = int(SystemSetting.get_setting('grade_b_plus', '70'))
        grade_b = int(SystemSetting.get_setting('grade_b', '60'))
        grade_c_plus = int(SystemSetting.get_setting('grade_c_plus', '55'))
        grade_c = int(SystemSetting.get_setting('grade_c', '50'))
        grade_d = int(SystemSetting.get_setting('grade_d', '40'))

        # Determine grade
        if percentage >= grade_a_plus:
            grade = 'A+'
        elif percentage >= grade_a:
            grade = 'A'
        elif percentage >= grade_b_plus:
            grade = 'B+'
        elif percentage >= grade_b:
            grade = 'B'
        elif percentage >= grade_c_plus:
            grade = 'C+'
        elif percentage >= grade_c:
            grade = 'C'
        elif percentage >= grade_d:
            grade = 'D'
        else:
            grade = 'F'
            
        subjects_set = set()
        exam_names_set = set()
        for r in results:
            if r.exam.subject:
                subjects_set.add(r.exam.subject.name)
            else:
                subjects_set.add(_('General'))
            exam_names_set.add(r.exam.exam_name)
            
        rankings.append({
            'student': student,
            'exams_taken': len(results),
            'total_obtained': total_obtained,
            'total_max': total_max,
            'percentage': round(percentage, 2),
            'grade': grade,
            'subjects': sorted(list(subjects_set)),
            'exam_names': sorted(list(exam_names_set))
        })
        
    # Sort rankings by percentage descending
    rankings.sort(key=lambda x: x['percentage'], reverse=True)
    
    return render_template('exams/rankings.html', rankings=rankings)
