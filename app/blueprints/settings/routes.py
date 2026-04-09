from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.settings import settings_bp
from .forms import GeneralSettingsForm, CategoryForm
from app.models.setting import SystemSetting
from app.models.category import Category
from app.extensions import db
from flask_babel import _

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'A':
        flash(_('You do not have permission to access this page.'), 'danger')
        return redirect(url_for('auth.dashboard'))
      
    form = GeneralSettingsForm()
    
    if form.validate_on_submit():
        SystemSetting.set_setting('rays_machad_name', form.rays_machad_name.data)
        SystemSetting.set_setting('rays_machad_address', form.rays_machad_address.data)
        SystemSetting.set_setting('rays_machad_phone', form.rays_machad_phone.data)
        SystemSetting.set_setting('rays_machad_email', form.rays_machad_email.data)
        SystemSetting.set_setting('active_term', form.active_term.data)
        SystemSetting.set_setting('currency', form.currency.data)
        SystemSetting.set_setting('whatsapp_access_token', form.whatsapp_access_token.data)
        SystemSetting.set_setting('whatsapp_phone_number_id', form.whatsapp_phone_number_id.data)
        SystemSetting.set_setting('whatsapp_mode', form.whatsapp_mode.data)
        
        # Save Grade Thresholds
        SystemSetting.set_setting('grade_a_plus', form.grade_a_plus.data)
        SystemSetting.set_setting('grade_a', form.grade_a.data)
        SystemSetting.set_setting('grade_b_plus', form.grade_b_plus.data)
        SystemSetting.set_setting('grade_b', form.grade_b.data)
        SystemSetting.set_setting('grade_c_plus', form.grade_c_plus.data)
        SystemSetting.set_setting('grade_c', form.grade_c.data)
        SystemSetting.set_setting('grade_d', form.grade_d.data)
        
        flash(_('System settings updated successfully.'), 'success')
        return redirect(url_for('settings.settings'))
    
    elif request.method == 'GET':
        form.rays_machad_name.data = SystemSetting.get_setting('rays_machad_name', 'Darul Arqam Rays Machad')
        form.rays_machad_address.data = SystemSetting.get_setting('rays_machad_address', '')
        form.rays_machad_phone.data = SystemSetting.get_setting('rays_machad_phone', '')
        form.rays_machad_email.data = SystemSetting.get_setting('rays_machad_email', '')
        form.active_term.data = SystemSetting.get_setting('active_term', 'Winter 2026')
        form.currency.data = SystemSetting.get_setting('currency', 'USD')
        form.whatsapp_access_token.data = SystemSetting.get_setting('whatsapp_access_token', '')
        form.whatsapp_phone_number_id.data = SystemSetting.get_setting('whatsapp_phone_number_id', '')
        form.whatsapp_mode.data = SystemSetting.get_setting('whatsapp_mode', 'mock')
        
        # Load Grade Thresholds (with defaults)
        form.grade_a_plus.data = int(SystemSetting.get_setting('grade_a_plus', '90'))
        form.grade_a.data = int(SystemSetting.get_setting('grade_a', '80'))
        form.grade_b_plus.data = int(SystemSetting.get_setting('grade_b_plus', '70'))
        form.grade_b.data = int(SystemSetting.get_setting('grade_b', '60'))
        form.grade_c_plus.data = int(SystemSetting.get_setting('grade_c_plus', '55'))
        form.grade_c.data = int(SystemSetting.get_setting('grade_c', '50'))
        form.grade_d.data = int(SystemSetting.get_setting('grade_d', '40'))
        
    return render_template('settings/index.html', form=form)

@settings_bp.route('/settings/permissions', methods=['GET', 'POST'])
@login_required
def manage_permissions():
    if current_user.role != 'A':
        flash(_('You do not have permission to access this page.'), 'danger')
        return redirect(url_for('auth.dashboard'))

    from app.models.permission import RolePermission

    roles = [
        ('T', _('Teacher')),
        ('S', _('Staff')),
        ('F', _('Finance')),
        ('P', _('Parent'))
    ]
    
    modules = [
        ('students', _('Students')),
        ('teachers', _('Teachers')),
        ('classes', _('Classes')),
        ('attendance', _('Attendance')),
        ('exams', _('Exams')),
        ('financials', _('Financials')),
        ('reports', _('Reports')),
        ('manage_users', _('Manage Users'))
    ]

    if request.method == 'POST':
        for role_code, role_name in roles:
            for mod_code, mod_name in modules:
                field_name = f"perm_{role_code}_{mod_code}"
                is_allowed = field_name in request.form
                RolePermission.set_permission(role_code, mod_code, is_allowed)
        
        flash(_('Permissions updated successfully.'), 'success')
        return redirect(url_for('settings.manage_permissions'))

    current_perms = {}
    for p in RolePermission.query.all():
        current_perms[f"{p.role}_{p.module}"] = p.is_allowed

    return render_template('settings/permissions.html', roles=roles, modules=modules, current_perms=current_perms)

@settings_bp.route('/settings/categories')
@login_required
def manage_categories():
    if current_user.role != 'A':
        flash(_('You do not have permission to access this page.'), 'danger')
        return redirect(url_for('auth.dashboard'))
    
    cat_type = request.args.get('type')
    query = Category.query
    if cat_type:
        query = query.filter_by(type=cat_type)
        
    categories = query.order_by(Category.type, Category.name).all()
    return render_template('settings/categories.html', categories=categories, current_type=cat_type)

@settings_bp.route('/settings/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if current_user.role != 'A':
        flash(_('You do not have permission to access this page.'), 'danger')
        return redirect(url_for('auth.dashboard'))
    
    cat_type = request.args.get('type')
    form = CategoryForm()
    
    if request.method == 'GET' and cat_type:
        form.type.data = cat_type

    if form.validate_on_submit():
        new_cat = Category(
            name=form.name.data,
            type=form.type.data,
            description=form.description.data
        )
        try:
            db.session.add(new_cat)
            db.session.commit()
            flash(_('Category added successfully.'), 'success')
            return redirect(url_for('settings.manage_categories', type=new_cat.type))
        except:
            db.session.rollback()
            flash(_('Error: Category already exists for this type.'), 'danger')
            
    return render_template('settings/category_form.html', form=form, current_type=cat_type)

@settings_bp.route('/settings/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if current_user.role != 'A':
        flash(_('You do not have permission to access this page.'), 'danger')
        return redirect(url_for('auth.dashboard'))
    
    cat = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=cat)
    
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.type = form.type.data
        cat.description = form.description.data
        try:
            db.session.commit()
            flash(_('Category updated successfully.'), 'success')
            return redirect(url_for('settings.manage_categories', type=cat.type))
        except:
            db.session.rollback()
            flash(_('Error updating category.'), 'danger')
            
    return render_template('settings/category_form.html', form=form, is_edit=True)

@settings_bp.route('/settings/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if current_user.role != 'A':
        flash(_('You do not have permission to access this page.'), 'danger')
        return redirect(url_for('auth.dashboard'))
    
    cat = Category.query.get_or_404(category_id)
    cat_type = cat.type
    db.session.delete(cat)
    db.session.commit()
    flash(_('Category deleted successfully.'), 'info')
    return redirect(url_for('settings.manage_categories', type=cat_type))

@settings_bp.route('/settings/logs')
@login_required
def message_logs():
    if current_user.role != 'A':
        flash(_('You do not have permission to access this page.'), 'danger')
        return redirect(url_for('auth.dashboard'))
    
    from app.models.message_log import MessageLog
    logs = MessageLog.query.order_by(MessageLog.sent_at.desc()).all()
    return render_template('settings/logs.html', logs=logs)
