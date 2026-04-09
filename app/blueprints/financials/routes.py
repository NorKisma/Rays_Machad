from flask import render_template, redirect, url_for, flash, request, abort, session, current_app
from app.blueprints.financials import financials_bp
from app.models.fee import Fee, Expense
from app.models.student import Student
from app.models.class_schedule import ClassSchedule
from app.extensions import db
from .forms import FeeForm, PaymentForm, ExpenseForm
from flask_login import login_required, current_user
from flask_babel import _
from datetime import datetime
from sqlalchemy import func
from app.models.setting import SystemSetting
from app.utils.decorators import permission_required
from app.ai_automation.notification_bot import NotificationBot
from app.utils.messaging import MessagingService
from app.models.attendance import Attendance
import calendar

@financials_bp.route('/receipt/<int:fee_id>')
@login_required
def view_receipt(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    
    # Permission Check
    is_authorized = False
    if current_user.role in ['A', 'F', 'S']:
        is_authorized = True
    elif current_user.role == 'P' and fee.student.parent_id == current_user.id:
        is_authorized = True
    elif current_user.role == 'U' and fee.student.student_user_id == current_user.id:
        is_authorized = True
        
    if not is_authorized:
        abort(403)

    rays_machad_name = SystemSetting.get_setting('rays_machad_name', 'Darul Arqam Rays Machad')
    rays_machad_address = SystemSetting.get_setting('rays_machad_address', '123 Islamic Center Way, City, Country')
    rays_machad_phone = SystemSetting.get_setting('rays_machad_phone', '+123 456 7890')
    
    return render_template('financials/receipt.html', 
                           fee=fee, 
                           rays_machad_name=rays_machad_name,
                           rays_machad_address=rays_machad_address,
                           rays_machad_phone=rays_machad_phone,
                           now=datetime.utcnow())

@financials_bp.route('/voucher/<int:expense_id>')
@permission_required('financials')
def view_voucher(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    rays_machad_name = SystemSetting.get_setting('rays_machad_name', 'Darul Arqam Rays Machad')
    rays_machad_address = SystemSetting.get_setting('rays_machad_address', '123 Islamic Center Way, City, Country')
    
    return render_template('financials/voucher.html', 
                           expense=expense,
                           rays_machad_name=rays_machad_name,
                           rays_machad_address=rays_machad_address,
                           now=datetime.utcnow())

@financials_bp.route('/')
@permission_required('financials')
def index():
    # Summary data
    total_fees_collected = db.session.query(func.sum(Fee.paid_amount)).scalar() or 0
    total_fees_pending = db.session.query(func.sum(Fee.balance)).scalar() or 0
    
    # Only count 'Paid' expenses towards actual expenses
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(Expense.status == 'Paid').scalar() or 0
    total_payables = db.session.query(func.sum(Expense.amount)).filter(Expense.status == 'Payable').scalar() or 0
    
    net_balance = total_fees_collected - total_expenses

    recent_fees = Fee.query.order_by(Fee.created_at.desc()).limit(5).all()
    recent_expenses = Expense.query.order_by(Expense.created_at.desc()).limit(5).all()

    from sqlalchemy import extract

    # Chart Data: Group by month for the current year
    current_year = datetime.utcnow().year
    
    # Income by month
    monthly_income_data = db.session.query(
        extract('month', Fee.payment_date).label('month'),
        func.sum(Fee.paid_amount).label('total')
    ).filter(
        Fee.payment_date != None,
        extract('year', Fee.payment_date) == current_year
    ).group_by('month').all()

    # Expenses by month
    monthly_expense_data = db.session.query(
        extract('month', Expense.expense_date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        extract('year', Expense.expense_date) == current_year
    ).group_by('month').all()

    # Convert to standard format (12 months)
    income_list = [0] * 12
    for m, t in monthly_income_data:
        income_list[int(m)-1] = float(t)

    expense_list = [0] * 12
    for m, t in monthly_expense_data:
        expense_list[int(m)-1] = float(t)

    # Create a unified transactions list for the professional dashboard table
    transactions = []
    for fee in recent_fees:
        transactions.append({
            'id': f'F-{fee.id}',
            'date': fee.created_at,
            'title': f"{fee.fee_type} - {fee.student.full_name}",
            'amount': float(fee.paid_amount) if fee.status != 'Unpaid' else float(fee.amount),
            'type': 'Inflow',
            'status': fee.status,
            'category': fee.fee_type,
            'raw_obj': fee
        })
    
    for exp in recent_expenses:
        transactions.append({
            'id': f'E-{exp.id}',
            'date': exp.created_at,
            'title': exp.title,
            'amount': float(exp.amount),
            'type': 'Outflow',
            'status': exp.status,
            'category': exp.category,
            'raw_obj': exp
        })
    
    # Sort unified transactions by date descending
    transactions.sort(key=lambda x: x['date'], reverse=True)

    return render_template('financials/index.html',
                           total_fees_collected=total_fees_collected,
                           total_fees_pending=total_fees_pending,
                           total_expenses=total_expenses,
                           total_payables=total_payables,
                           net_balance=net_balance,
                           recent_fees=recent_fees,
                           recent_expenses=recent_expenses,
                           transactions=transactions,
                           income_list=income_list,
                           expense_list=expense_list)

@financials_bp.route('/fees')
@permission_required('financials')
def manage_fees():
    status = request.args.get('status')
    if status:
        fees = Fee.query.filter_by(status=status).order_by(Fee.due_date.desc()).all()
    else:
        fees = Fee.query.order_by(Fee.due_date.desc()).all()
    return render_template('financials/fees.html', fees=fees, current_status=status)

@financials_bp.route('/fees/add', methods=['GET', 'POST'])
@financials_bp.route('/fees/add/<int:student_id>', methods=['GET', 'POST'])
@permission_required('financials')
def add_fee(student_id=None):
    form = FeeForm()
    students = Student.query.filter_by(status='Active').all()
    form.student_id.choices = [(s.id, f"{s.full_name} ({s.enrollment_number})") for s in students]

    if request.method == 'GET' and student_id:
        form.student_id.data = student_id
        # Pre-fill amount based on student's specific monthly fee or class tuition fee
        student = Student.query.get(student_id)
        if student:
            # Use student's custom monthly fee if set (> 0), otherwise use class tuition fee
            if student.monthly_fee and student.monthly_fee > 0:
                form.amount.data = float(student.monthly_fee)
            elif student.class_assigned:
                form.amount.data = float(student.class_assigned.tuition_fee or 0)
            else:
                form.amount.data = 0
                
            form.fee_type.data = 'Tuition'
            form.fee_month.data = datetime.utcnow().strftime('%B %Y')
            form.due_date.data = datetime.utcnow().date()

    if form.validate_on_submit():
        new_fee = Fee(
            student_id=form.student_id.data,
            amount=form.amount.data,
            balance=form.amount.data,
            fee_type=form.fee_type.data,
            fee_month=form.fee_month.data,
            due_date=form.due_date.data,
            status='Unpaid',
            paid_amount=0,
            remarks=form.remarks.data
        )
        db.session.add(new_fee)
        db.session.commit()
        flash(_("Fee record added successfully!"), 'success')
        return redirect(url_for('financials.manage_fees'))
    
    return render_template('financials/fee_form.html', form=form, title=_("Add New Fee"))

@financials_bp.route('/fees/pay/<int:fee_id>', methods=['GET', 'POST'])
@permission_required('financials')
def pay_fee(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    if fee.status == 'Paid':
        flash(_("This fee is already paid."), 'info')
        return redirect(url_for('financials.manage_fees'))

    form = PaymentForm()
    if form.validate_on_submit():
        paid_val = form.amount_paid.data
        
        if paid_val <= 0:
            flash(_("Payment amount must be greater than zero."), 'danger')
            return render_template('financials/payment_form.html', form=form, fee=fee)

        if paid_val > fee.balance:
            flash(_("Payment amount cannot exceed the remaining balance."), 'danger')
            return render_template('financials/payment_form.html', form=form, fee=fee)

        fee.paid_amount = (fee.paid_amount or 0) + paid_val
        fee.balance = fee.amount - fee.paid_amount
        
        if fee.balance <= 0:
            fee.status = 'Paid'
        else:
            fee.status = 'Partial'
            
        fee.payment_date = datetime.combine(form.payment_date.data, datetime.min.time())
        fee.payment_method = form.payment_method.data
        fee.transaction_id = form.transaction_id.data
        
        # Log payment in remarks
        pay_info = f"\n[{fee.payment_date.strftime('%Y-%m-%d')}] Paid: {paid_val} via {fee.payment_method}"
        fee.remarks = (fee.remarks or "") + pay_info
        
        db.session.commit()
        flash(_("Payment recorded successfully!"), 'success')
        return redirect(url_for('financials.view_receipt', fee_id=fee.id))
    
    if request.method == 'GET':
        form.payment_date.data = datetime.utcnow().date()
        form.amount_paid.data = fee.balance
        from app.utils.generators import generate_transaction_id
        form.transaction_id.data = generate_transaction_id()

    return render_template('financials/payment_form.html', form=form, fee=fee)

@financials_bp.route('/expenses')
@permission_required('financials')
def manage_expenses():
    expenses = Expense.query.order_by(Expense.expense_date.desc()).all()
    return render_template('financials/expenses.html', expenses=expenses)

@financials_bp.route('/payables')
@permission_required('financials')
def manage_payables():
    expenses = Expense.query.filter_by(status='Payable').order_by(Expense.expense_date.desc()).all()
    return render_template('financials/payables.html', expenses=expenses)

@financials_bp.route('/expenses/add', methods=['GET', 'POST'])
@permission_required('financials')
def add_expense():
    from app.models.teacher import Teacher
    form = ExpenseForm()
    
    # Populate teacher and category choices
    from app.models.category import Category
    form.teacher_id.choices = [(0, _('N/A (General Expense)'))] + [(t.id, t.full_name) for t in Teacher.query.order_by('full_name').all()]
    form.category.choices = [(c.name, c.name) for c in Category.query.filter_by(type='Expense').all()]
    if not form.category.choices:
        form.category.choices = [('Other', _('Other'))]
    
    if form.validate_on_submit():
        new_expense = Expense(
            title=form.title.data,
            category=form.category.data,
            amount=form.amount.data,
            expense_date=form.expense_date.data,
            payment_method=form.payment_method.data,
            status=form.status.data,
            description=form.description.data,
            teacher_id=form.teacher_id.data if form.teacher_id.data != 0 else None
        )
        db.session.add(new_expense)
        db.session.commit()
        flash(_("Expense recorded successfully!"), 'success')
        return redirect(url_for('financials.manage_expenses'))
    
    if request.method == 'GET':
        form.expense_date.data = datetime.utcnow().date()

    return render_template('financials/expense_form.html', form=form)

@financials_bp.route('/structures')
@permission_required('financials')
def manage_structures():
    classes = ClassSchedule.query.all()
    return render_template('financials/structures.html', classes=classes)

@financials_bp.route('/structures/update/<int:class_id>', methods=['POST'])
@permission_required('financials')
def update_structure(class_id):
    cls = ClassSchedule.query.get_or_404(class_id)
    try:
        cls.tuition_fee = request.form.get('tuition_fee', 0)
        cls.admission_fee = request.form.get('admission_fee', 0)
        cls.exam_fee = request.form.get('exam_fee', 0)
        cls.uniform_fee = request.form.get('uniform_fee', 0)
        cls.books_fee = request.form.get('books_fee', 0)
        cls.bus_fee = request.form.get('bus_fee', 0)
        cls.activity_fee = request.form.get('activity_fee', 0)
        cls.library_fee = request.form.get('library_fee', 0)
        cls.other_fee = request.form.get('other_fee', 0)
        db.session.commit()
        flash(_("Fee structure for %(name)s updated successfully!", name=cls.class_name), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_("Error updating fee structure: %(error)s", error=str(e)), 'danger')
        
    return redirect(url_for('financials.manage_structures'))

def generate_fees_logic():
    today = datetime.utcnow()
    # Use standard format for duplicate checking (Language neutral)
    month_id = today.strftime('%Y-%m')
    display_month = today.strftime('%B %Y')
    
    # Get all active students
    active_students = Student.query.filter(Student.status == 'Active').all()
    
    generated_count = 0
    already_billed_count = 0
    no_fee_set_count = 0
    
    due_date = today.replace(day=5).date()
    
    for student in active_students:
        # Priority 1: Individual Student Monthly Fee
        # Priority 2: Class-based Tuition Fee
        fee_amount = student.monthly_fee or 0
        
        if fee_amount <= 0 and student.class_assigned:
            fee_amount = student.class_assigned.tuition_fee or 0
            
        if fee_amount <= 0:
            no_fee_set_count += 1
            continue
            
        # Check if already billed for this specific month
        existing_fee = Fee.query.filter(
            Fee.student_id == student.id,
            Fee.fee_type == 'Tuition',
            Fee.fee_month == month_id
        ).first()
        
        if not existing_fee:
            new_fee = Fee(
                student_id=student.id,
                amount=fee_amount,
                balance=fee_amount,
                paid_amount=0,
                fee_type='Tuition',
                fee_month=month_id,
                due_date=due_date,
                status='Unpaid',
                remarks=_("Automatically generated for %(month)s", month=display_month)
            )
            db.session.add(new_fee)
            generated_count += 1
        else:
            already_billed_count += 1
            
    db.session.commit()
    
    return {
        'generated': generated_count,
        'already_billed': already_billed_count,
        'no_fee_set': no_fee_set_count,
        'month': display_month,
        'total_active': len(active_students)
    }

@financials_bp.route('/generate-monthly-fees', methods=['POST'])
@permission_required('financials')
def generate_monthly_fees():
    stats = generate_fees_logic()
    
    if stats['generated'] > 0:
        flash(_("<strong>Success!</strong> Generated %(count)s tuition records for %(month)s.", 
                count=stats['generated'], month=stats['month']), 'success')
    else:
        # Provide "suitable options" and detailed info in a more structured way
        if stats['total_active'] == 0:
            flash(_("<strong>Notice:</strong> There are no active students in the system. Registration is required first."), 'warning')
        elif stats['already_billed'] == stats['total_active']:
            flash(_("<strong>All Set!</strong> Fees for %(month)s have already been generated for all active students."), 'info')
        else:
            msg = _("<strong>No new fees generated.</strong> Check these suitable options:<br>")
            if stats['no_fee_set'] > 0:
                msg += f'• {_("%(count)s students have no tuition fee set.", count=stats["no_fee_set"])} '
                msg += f'<a href="{url_for("financials.manage_structures")}" class="alert-link">{_("Set Fee Structures")}</a><br>'
            
            # Check for students without classes
            missing_class_count = db.session.query(func.count(Student.id)).filter(Student.status == 'Active', Student.class_id == None).scalar()
            if missing_class_count > 0:
                msg += f'• {_("%(count)s students have no class assigned.", count=missing_class_count)} '
                msg += f'<a href="{url_for("students.manage_students")}" class="alert-link">{_("Assign Classes")}</a>'
            
            flash(msg, 'info')
        
    return redirect(url_for('financials.index'))
@financials_bp.route('/fees/delete/<int:fee_id>', methods=['POST'])
@permission_required('financials')
def delete_fee(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    db.session.delete(fee)
    db.session.commit()
    flash(_("Fee record deleted successfully!"), 'warning')
    return redirect(url_for('financials.manage_fees'))

@financials_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@permission_required('financials')
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash(_("Expense record deleted successfully!"), 'warning')
    return redirect(url_for('financials.manage_expenses'))

@financials_bp.route('/pay-expense/<int:expense_id>', methods=['POST'])
@permission_required('financials')
def pay_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.status == 'Payable':
        expense.status = 'Paid'
        expense.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('Expense marked as Paid successfully'), 'success')
    return redirect(request.referrer or url_for('financials.manage_expenses'))
@financials_bp.route('/send-monthly-reports', methods=['POST'])
@permission_required('financials')
def send_monthly_reports():
    """
    Send AI-generated monthly reports to all active students' parents.
    This version is defensive: any unexpected error is logged and surfaced
    via flash messages instead of causing a 500 error.
    """
    try:
        bot = NotificationBot()
        messenger = MessagingService()
        
        today = datetime.utcnow()
        month_id = today.strftime('%Y-%m')
        display_month = today.strftime('%B %Y')
        
        # Get the date range for the current month to calculate attendance
        year, month = today.year, today.month
        first_day = today.replace(day=1).date()
        last_day_num = calendar.monthrange(year, month)[1]
        last_day = today.replace(day=last_day_num).date()

        active_students = Student.query.filter(Student.status == 'Active').all()
        sent_count = 0
        errors = 0
        skipped_no_phone = 0

        last_sent_error = None
        for student in active_students:
            # Skip if no parent contact is available
            if not getattr(student, "parent_contact", None):
                skipped_no_phone += 1
                continue

            # Attendance stats for the month
            total_days = Attendance.query.filter(
                Attendance.student_id == student.id,
                Attendance.attendance_date >= first_day,
                Attendance.attendance_date <= last_day
            ).count()
            
            present_days = Attendance.query.filter(
                Attendance.student_id == student.id,
                Attendance.attendance_date >= first_day,
                Attendance.attendance_date <= last_day,
                Attendance.status == 'Present'
            ).count()
            
            att_pct = (present_days / total_days * 100) if total_days > 0 else 0
            current_fee = Fee.query.filter(
                Fee.student_id == student.id,
                Fee.fee_month == month_id
            ).first()
            
            status = current_fee.status if current_fee else 'N/A'
            balance = current_fee.balance if current_fee else 0
            
            report_data = {
                'month': display_month,
                'attendance': round(att_pct or 0, 1),
                'juz': student.current_juz or 1,
                'surah': student.current_surah or 'N/A',
                'fee_status': status,
                'balance': float(balance),
                'lang': session.get('lang') or request.accept_languages.best_match(['en', 'so', 'ar']) or 'en'
            }
            
            parent_name = student.father_name or student.mother_name or _("Parent")
            student_name = student.full_name
            
            message = bot.generate_monthly_report(parent_name, student_name, report_data)
            success, info = messenger.send_ai_report(parent_name, student.parent_contact, message)
            
            if success:
                sent_count += 1
            else:
                errors += 1
                last_sent_error = info
        
        if sent_count > 0:
            flash(_("Successfully sent %(count)s monthly reports to parents via AI Messaging.", count=sent_count), 'success')
        if skipped_no_phone > 0:
            flash(_("Skipped %(count)s students because no parent phone number was set.", count=skipped_no_phone), 'info')
        if errors > 0:
            flash(_("Failed to send %(count)s reports. Error: %(error)s", count=errors, error=str(last_sent_error)), 'warning')

    except Exception as e:
        current_app.logger.exception("Error while sending monthly AI reports")
        flash(_("An unexpected error occurred while sending monthly reports: %(error)s", error=str(e)), 'danger')

    return redirect(url_for('financials.index'))
@financials_bp.route('/generate-salaries', methods=['POST'])
@permission_required('financials')
def generate_salaries():
    from app.models.teacher import Teacher
    today = datetime.utcnow()
    month_id = today.strftime('%Y-%m')
    display_month = today.strftime('%B %Y')
    
    # Get all active teachers
    active_teachers = Teacher.query.filter(Teacher.status == 'Active').all()
    
    generated_count = 0
    already_paid_count = 0
    no_salary_set_count = 0
    
    for teacher in active_teachers:
        salary_amount = teacher.monthly_salary or 0
            
        if salary_amount <= 0:
            no_salary_set_count += 1
            continue
            
        # Check if already paid for this specific month using language-neutral ID
        existing_salary = Expense.query.filter(
            Expense.teacher_id == teacher.id,
            Expense.category == 'Salary',
            Expense.expense_month == month_id
        ).first()
        
        if not existing_salary:
            new_expense = Expense(
                title=f"{_('Salary')}: {teacher.full_name}",
                category='Salary',
                amount=salary_amount,
                expense_date=today.date(),
                payment_method='Cash', # Default
                status='Payable',      # Marked as payable account
                transaction_id=None,
                expense_month=month_id,
                description=f"{_('Generated Salary for')} {display_month}",
                teacher_id=teacher.id
            )
            db.session.add(new_expense)
            generated_count += 1
        else:
            already_paid_count += 1
            
    db.session.commit()
    
    if generated_count > 0:
        flash(_("Successfully generated %(count)s salary records for %(month)s.", count=generated_count, month=display_month), 'success')
    else:
        if already_paid_count == len(active_teachers) and len(active_teachers) > 0:
            flash(_("All teacher salaries for %(month)s have already been generated.", month=display_month), 'info')
        else:
            flash(_("No new salaries generated. Check if teachers have salaries set."), 'warning')
            
    return redirect(url_for('financials.index'))
