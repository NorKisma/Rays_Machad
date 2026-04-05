from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.blueprints.classes import classes_bp
from app.models.class_schedule import ClassSchedule
from app.models.teacher import Teacher
from app.models.subject import Subject
from .forms import ClassForm, SubjectForm
from app.models.category import Category
from app.extensions import db
from flask_babel import _
from app.utils.decorators import admin_required, staff_required, teacher_required
from flask import abort

@classes_bp.route("/")
@teacher_required
def manage_classes():
    from app.models.category import Category
    # Filter if user is a teacher
    if current_user.role == 'T' and current_user.teacher_profile:
        classes = ClassSchedule.query.filter_by(teacher_id=current_user.teacher_profile.id).all()
    elif current_user.role == 'T':
        classes = []
    else:
        classes = ClassSchedule.query.all()
        
    categories = Category.query.filter_by(type='Subject').all()
    return render_template("classes/manage_classes.html", classes=classes, categories=categories)

@classes_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_class():
    form = ClassForm()
    # Populate teachers dropdown
    form.teacher_id.choices = [(0, _('Select Teacher'))] + [(t.id, t.full_name) for t in Teacher.query.filter_by(status='Active').all()]
    
    if form.validate_on_submit():
        new_class = ClassSchedule(
            class_name=form.class_name.data,
            description=form.description.data,
            teacher_id=form.teacher_id.data,

        )
        db.session.add(new_class)
        db.session.commit()
        flash(_("Class created successfully!"), "success")
        return redirect(url_for("classes.manage_classes"))
        
    return render_template("classes/add_class.html", form=form)

@classes_bp.route("/edit/<int:class_id>", methods=["GET", "POST"])
@admin_required
def edit_class(class_id):
    cls = ClassSchedule.query.get_or_404(class_id)
    form = ClassForm(obj=cls)
    # Populate teachers dropdown
    form.teacher_id.choices = [(0, _('Select Teacher'))] + [(t.id, t.full_name) for t in Teacher.query.filter_by(status='Active').all()]
    
    if form.validate_on_submit():
        cls.class_name = form.class_name.data
        cls.description = form.description.data
        cls.teacher_id = form.teacher_id.data

        db.session.commit()
        flash(_("Class updated successfully!"), "success")
        return redirect(url_for("classes.manage_classes"))
        
    return render_template("classes/add_class.html", form=form, is_edit=True)

@classes_bp.route("/schedule/<int:class_id>", methods=["GET", "POST"])
@teacher_required
def view_schedule(class_id):
    from app.models.session import ClassSession
    from .forms import ClassSessionForm
    from datetime import time
    
    cls = ClassSchedule.query.get_or_404(class_id)
    
    # Permission Check
    if current_user.role == 'T':
        if not current_user.teacher_profile or cls.teacher_id != current_user.teacher_profile.id:
            abort(403)
            
    form = ClassSessionForm()
    
    if form.validate_on_submit():
        try:
            # Parse times
            st = [int(x) for x in form.start_time.data.split(':')]
            et = [int(x) for x in form.end_time.data.split(':')]
            
            new_session = ClassSession(
                class_id=class_id,
                day_of_week=form.day_of_week.data,
                start_time=time(st[0], st[1]),
                end_time=time(et[0], et[1]),
                room=form.room.data
            )
            db.session.add(new_session)
            db.session.commit()
            flash(_("New session added to schedule!"), "success")
            return redirect(url_for("classes.view_schedule", class_id=class_id))
        except Exception as e:
            db.session.rollback()
            flash(_("Error adding session. Ensure time format is HH:MM"), "danger")
            
    sessions = ClassSession.query.filter_by(class_id=class_id).all()
    return render_template("classes/view_schedule.html", cls=cls, form=form, sessions=sessions)

@classes_bp.route("/session/delete/<int:session_id>", methods=["POST"])
@admin_required
def delete_session(session_id):
    from app.models.session import ClassSession
    session_obj = ClassSession.query.get_or_404(session_id)
    class_id = session_obj.class_id
    db.session.delete(session_obj)
    db.session.commit()
    flash(_("Session removed from schedule."), "warning")
    return redirect(url_for("classes.view_schedule", class_id=class_id))

# --- SUBJECT MANAGEMENT ---

@classes_bp.route("/subjects")
@staff_required
def manage_subjects():
    subjects = Subject.query.all()
    return render_template("classes/manage_subjects.html", subjects=subjects)

@classes_bp.route("/subjects/add", methods=["GET", "POST"])
@admin_required
def add_subject():
    form = SubjectForm()
    # Populate categories from DB
    form.category.choices = [(c.name, c.name) for c in Category.query.filter_by(type='Subject').all()]
    if not form.category.choices:
        form.category.choices = [('Other', _('Other'))]
    if form.validate_on_submit():
        new_subject = Subject(
            name=form.name.data,
            code=form.code.data,
            category=form.category.data,
            description=form.description.data
        )
        try:
            db.session.add(new_subject)
            db.session.commit()
            flash(_("Subject created successfully!"), "success")
            return redirect(url_for("classes.manage_subjects"))
        except Exception as e:
            db.session.rollback()
            flash(_("Error creating subject. Code/Name might already exist."), "danger")
            
    return render_template("classes/subject_form.html", form=form)

@classes_bp.route("/subjects/edit/<int:subject_id>", methods=["GET", "POST"])
@admin_required
def edit_subject(subject_id):
    subj = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subj)
    # Populate categories from DB
    form.category.choices = [(c.name, c.name) for c in Category.query.filter_by(type='Subject').all()]
    if not form.category.choices:
        form.category.choices = [('Other', _('Other'))]
    
    if form.validate_on_submit():
        subj.name = form.name.data
        subj.code = form.code.data
        subj.category = form.category.data
        subj.description = form.description.data
        
        try:
            db.session.commit()
            flash(_("Subject updated successfully!"), "success")
            return redirect(url_for("classes.manage_subjects"))
        except:
            db.session.rollback()
            flash(_("Error updating subject."), "danger")
            
    return render_template("classes/subject_form.html", form=form, is_edit=True)

@classes_bp.route("/subjects/delete/<int:subject_id>", methods=["POST"])
@admin_required
def delete_subject(subject_id):
    subj = Subject.query.get_or_404(subject_id)
    db.session.delete(subj)
    db.session.commit()
    flash(_("Subject deleted successfully."), "info")
    return redirect(url_for("classes.manage_subjects"))
