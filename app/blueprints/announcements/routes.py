from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.announcements import announcements_bp
from app.models.announcement import Announcement
from app.blueprints.announcements.forms import AnnouncementForm
from app.extensions import db
from app.utils.decorators import admin_required, permission_required
from flask_babel import _
from datetime import datetime


@announcements_bp.route('/')
@login_required
def index():
    # Only Admin and Staff can manage announcements, others just see them
    if current_user.role in ['A', 'S']:
        announcements = Announcement.query.order_by(
            Announcement.created_at.desc()
        ).all()
        return render_template(
            'announcements/manage.html',
            announcements=announcements
        )

    # Generic view for others
    announcements = Announcement.query.filter(
        (Announcement.target_audience == 'All') |
       
Announcement.target_audience == current_user.role + 's'


    ).order_by(Announcement.created_at.desc()).all()

    return render_template(
        'announcements/index.html',
        announcements=announcements
    )


@announcements_bp.route('/add', methods=['GET', 'POST'])
@permission_required('manage_users')
def add():
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            target_audience=form.target_audience.data,
            priority=form.priority.data,
            expires_at=form.expires_at.data,
            created_by_id=current_user.id
        )
        db.session.add(announcement)
        db.session.commit()
        flash(_('Announcement posted successfully!'), 'success')
        return redirect(url_for('announcements.index'))

    return render_template(
        'announcements/form.html',
        form=form,
        title=_('Add Announcement')
    )


@announcements_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@permission_required('manage_users')
def edit(id):
    announcement = Announcement.query.get_or_404(id)
    form = AnnouncementForm(obj=announcement)

    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.content = form.content.data
        announcement.target_audience = form.target_audience.data
        announcement.priority = form.priority.data
        announcement.expires_at = form.expires_at.data
        db.session.commit()
        flash(_('Announcement updated successfully!'), 'success')
        return redirect(url_for('announcements.index'))

    return render_template(
        'announcements/form.html',
        form=form,
        title=_('Edit Announcement')
    )


@announcements_bp.route('/broadcast/<int:id>', methods=['POST'])
@permission_required('manage_users')
def broadcast_whatsapp(id):
    from app.models.student import Student
    from app.models.teacher import Teacher
    from app.utils.messaging import MessagingService
    
    announcement = Announcement.query.get_or_404(id)
    messenger = MessagingService()
    
    target_numbers = set()
    
    # 1. Collect Parent Numbers if audience is 'All' or 'Parents'
    if announcement.target_audience in ['All', 'Parents']:
        active_students = Student.query.filter(Student.status == 'Active').all()
        for s in active_students:
            if s.parent_contact:
                target_numbers.add(s.parent_contact)
                
    # 2. Collect Teacher Numbers if audience is 'All' or 'Teachers'
    if announcement.target_audience in ['All', 'Teachers']:
        active_teachers = Teacher.query.filter(Teacher.status == 'Active').all()
        for t in active_teachers:
            if t.phone:
                target_numbers.add(t.phone)
    
    sent_count = 0
    errors = 0
    last_error = None
    
    # Format message based on audience
    header = _("OGAYSIIS MUHIIM AH")
    if announcement.target_audience == 'Teachers':
        header = _("OGAYSIIS MACALIMIINTA")
    elif announcement.target_audience == 'Parents':
        header = _("OGAYSIIS WAALIDIINTA")
        
    message = f"*{header}*\n\n{announcement.title.upper()}\n\n{announcement.content}"
    
    for number in target_numbers:
        success, info = messenger.send_whatsapp(number, message, msg_type='announcement')
        if success:
            sent_count += 1
        else:
            errors += 1
            last_error = info
            
    if sent_count > 0:
        flash(_("Successfully broadcasted announcement to %(count)s recipients via WhatsApp.", count=sent_count), 'success')
    if errors > 0:
        flash(_("Failed to send to %(count)s numbers. Details: %(error)s", count=errors, error=str(last_error)), 'warning')
        
    return redirect(url_for('announcements.index'))


@announcements_bp.route('/delete/<int:id>', methods=['POST'])
@permission_required('manage_users')
def delete(id):
    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    flash(_('Announcement deleted!'), 'warning')
    return redirect(url_for('announcements.index'))
