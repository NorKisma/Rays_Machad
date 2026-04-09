from flask import render_template, request
from app.blueprints.reports import reports_bp
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.fee import Fee, Expense
from app.models.class_schedule import ClassSchedule
from app.extensions import db
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from flask_babel import _
from sqlalchemy import func
from datetime import datetime

@reports_bp.route('/')
@login_required
def index():
    # Only Admin, Staff and Teachers can see reports
    if current_user.role not in ['A', 'S', 'T']:
        return render_template('errors/403.html'), 403

    # Stats for overview
    if current_user.role == 'T' and current_user.teacher_profile:
        # Teacher-specific stats
        my_classes = ClassSchedule.query.filter_by(teacher_id=current_user.teacher_profile.id).all()
        total_classes = len(my_classes)
        total_students = sum(len(c.students) for c in my_classes)
        active_students = sum(len([s for s in c.students if s.status == 'Active']) for c in my_classes)
        total_teachers = 1
    else:
        total_students = Student.query.count()
        active_students = Student.query.filter_by(status='Active').count()
        total_teachers = Teacher.query.count()
        total_classes = ClassSchedule.query.count()
    
    # Financial Stats (Hidden for Teachers)
    total_collected = 0
    total_unpaid = 0
    total_expenses = 0
    if current_user.role in ['A', 'S']:
        total_collected = db.session.query(func.sum(Fee.amount)).filter(Fee.status == 'Paid').scalar() or 0
        total_unpaid = db.session.query(func.sum(Fee.amount)).filter(Fee.status == 'Unpaid').scalar() or 0
        total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    
    # Reports list for the UI
    all_reports = [
        {
            'id': 'attendance',
            'title': _('Attendance Analytics'),
            'description': _('Daily and monthly attendance trends for all classes.'),
            'icon': 'fa-clipboard-check',
            'color': 'info',
            'link': 'attendance.index'
        },
        {
            'id': 'exams',
            'title': _('Examination Results'),
            'description': _('Academic performance reports and merit lists.'),
            'icon': 'fa-square-poll-vertical',
            'color': 'warning',
            'link': 'exams.manage_exams'
        },
        {
            'id': 'students',
            'title': _('Student Directory Roster'),
            'description': _('Official printable list of all registered students with full academic and personal details.'),
            'icon': 'fa-user-graduate',
            'color': 'primary',
            'link': 'students.print_all_students'
        },
        {
            'id': 'teachers',
            'title': _('Staff & Teacher Directory'),
            'description': _('Professional roster of all Rays Machad staff members with qualifications and contact info.'),
            'icon': 'fa-user-tie',
            'color': 'dark',
            'link': 'teachers.print_all_teachers'
        },
        {
            'id': 'fees',
            'title': _('Fee Collection Report'),
            'description': _('Detailed report of all paid and unpaid fees across the system.'),
            'icon': 'fa-money-bill-trend-up',
            'color': 'success',
            'link': 'financials.manage_fees'
        },
        {
            'id': 'expenses',
            'title': _('Expense Tracking Report'),
            'description': _('Full breakdown of all operational expenses recorded.'),
            'icon': 'fa-file-invoice-dollar',
            'color': 'danger',
            'link': 'financials.manage_expenses'
        },
        {
            'id': 'profit_loss',
            'title': _('Profit & Loss Report'),
            'description': _('Monthly and yearly financial performance breakdown for the institution.'),
            'icon': 'fa-chart-pie',
            'color': 'indigo',
            'link': 'reports.profit_loss'
        }
    ]

    # Filter reports based on role
    if current_user.role == 'T':
        reports = [r for r in all_reports if r['id'] in ['attendance', 'exams', 'students']]
    else:
        reports = all_reports

    return render_template('reports/index.html', 
                           reports=reports,
                           total_students=total_students,
                           active_students=active_students,
                           total_teachers=total_teachers,
                           total_classes=total_classes,
                           total_collected=total_collected,
                           total_unpaid=total_unpaid,
                           total_expenses=total_expenses)
@reports_bp.route('/profit-loss')
@login_required
def profit_loss():
    if current_user.role not in ['A', 'S']:
        return render_template('errors/403.html'), 403

    year = request.args.get('year', datetime.utcnow().year, type=int)
    month = request.args.get('month', type=int) # Optional month filter
    
    # Get all months for the selected year for the summary
    months_data = {}
    for m in range(1, 13):
        month_key = f"{year}-{str(m).zfill(2)}"
        months_data[month_key] = {'income': 0, 'expense': 0, 'profit': 0, 'month_name': _(datetime(year, m, 1).strftime('%B'))}

    # Fetch Income (Paid Fees)
    income_query = Fee.query.filter(Fee.status == 'Paid', func.year(Fee.payment_date) == year)
    if month:
        income_query = income_query.filter(func.month(Fee.payment_date) == month)
    
    income_records = income_query.all()
    
    # Fetch Expenses
    expense_query = Expense.query.filter(func.year(Expense.expense_date) == year)
    if month:
        expense_query = expense_query.filter(func.month(Expense.expense_date) == month)
    
    expense_records = expense_query.all()

    # Process summary for all months in that year
    all_income = Fee.query.filter(Fee.status == 'Paid', func.year(Fee.payment_date) == year).all()
    all_expenses = Expense.query.filter(func.year(Expense.expense_date) == year).all()

    for record in all_income:
        if record.payment_date:
            key = f"{year}-{str(record.payment_date.month).zfill(2)}"
            if key in months_data:
                months_data[key]['income'] += float(record.amount)

    for record in all_expenses:
        key = f"{year}-{str(record.expense_date.month).zfill(2)}"
        if key in months_data:
            months_data[key]['expense'] += float(record.amount)

    # Process Transaction Log (combined and sorted)
    transactions = []
    for r in income_records:
        transactions.append({
            'date': r.payment_date,
            'type': 'Credit',
            'category': r.fee_type,
            'description': f"{r.student.full_name} ({r.fee_month or _('Fee')})",
            'amount': float(r.amount),
            'ref': r.transaction_id or f"FEE-{r.id}"
        })
    
    for r in expense_records:
        transactions.append({
            'date': r.expense_date,
            'type': 'Debit',
            'category': r.category,
            'description': r.title,
            'status': getattr(r, 'status', 'Paid'),
            'amount': float(r.amount),
            'ref': f"EXP-{r.id}"
        })
    
    # Sort transactions by date descending
    def sort_key(x):
        d = x['date']
        if d is None:
            return datetime.min.date()
        if isinstance(d, datetime):
            return d.date()
        return d

    transactions.sort(key=sort_key, reverse=True)

    # Calculation for summary
    total_income = 0
    total_expense = 0
    total_payable = 0
    for key in months_data:
        months_data[key]['profit'] = months_data[key]['income'] - months_data[key]['expense']
        total_income += months_data[key]['income']
        total_expense += months_data[key]['expense']
    
    # Calculate payables separately for the summary
    total_payable = sum(float(r.amount) for r in all_expenses if getattr(r, 'status', 'Paid') == 'Payable')

    # Specific totals for the selected period (month or year)
    if month:
        period_income = sum(t['amount'] for t in transactions if t['type'] == 'Credit')
        period_expense = sum(t['amount'] for t in transactions if t['type'] == 'Debit')
    else:
        period_income = total_income
        period_expense = total_expense

    sorted_months = sorted(months_data.items())

    # Available filters
    income_years = db.session.query(func.year(Fee.payment_date)).filter(Fee.status == 'Paid').distinct().all()
    expense_years = db.session.query(func.year(Expense.expense_date)).distinct().all()
    available_years = sorted(list(set([y[0] for y in income_years if y[0]] + [y[0] for y in expense_years if y[0]] + [datetime.utcnow().year])), reverse=True)

    return render_template('reports/profit_loss.html', 
                           months=sorted_months,
                           transactions=transactions,
                           total_income=total_income,
                           total_expense=total_expense,
                           total_payable=total_payable,
                           period_income=period_income,
                           period_expense=period_expense,
                           net_profit=total_income - total_expense,
                           selected_year=year,
                           selected_month=month,
                           available_years=available_years,
                           datetime=datetime)
