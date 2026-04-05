from flask import render_template, redirect, url_for, flash, request, session
from app.blueprints.onboarding import onboarding_bp
from app.models.school import School
from app.models.user import User
from app.extensions import db

from app.utils.payments import IPayService

@onboarding_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        school_name = request.form.get("school_name")
        subdomain = request.form.get("subdomain").lower().strip()
        admin_email = request.form.get("admin_email").lower().strip()
        password = request.form.get("password")
        payment_phone = request.form.get("payment_phone")
        requested_amount = request.form.get("requested_amount")
        
        # Validation
        if School.query.filter_by(subdomain=subdomain).first():
            flash("Subdomain already taken. Please choose another one.", "danger")
            return redirect(url_for("onboarding.register"))
            
        if User.query.filter_by(email=admin_email).first():
            flash("Email already registered. Please use another email.", "danger")
            return redirect(url_for("onboarding.register"))
            
        try:
            # 1. Create School (Pending)
            new_school = School(
                name=school_name,
                subdomain=subdomain,
                admin_email=admin_email,
                payment_phone=payment_phone,
                requested_amount=requested_amount,
                is_active=False,
                status='Pending'
            )
            db.session.add(new_school)
            db.session.flush() # Get school ID
            
            # 2. Create Admin User
            new_user = User(
                name=f"{school_name} Admin",
                email=admin_email,
                role='A',
                school_id=new_school.id,
                is_active=True
            )
            new_user.set_password(password)
            db.session.add(new_user)
            
            db.session.commit()
            
            # Redirect to Payment Page
            return redirect(url_for("onboarding.payment", school_id=new_school.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {str(e)}", "danger")
            
    return render_template("onboarding/register.html")

@onboarding_bp.route("/payment/<int:school_id>", methods=["GET", "POST"])
def payment(school_id):
    school = School.query.get_or_404(school_id)
    
    if request.method == "POST":
        phone = request.form.get("phone")
        plan = request.form.get("plan", "Basic")
        amount = 15 if plan == "Basic" else 30
        
        ipay = IPayService()
        success, response = ipay.initiate_payment(phone, amount, f"Plan: {plan} - {school.name}")
        
        if success:
            # Save payment info - but do NOT activate yet
            school.subscription_plan = plan
            school.payment_transaction_id = response.get('transactionId') if isinstance(response, dict) else None
            school.last_payment_status = 'Pending'
            # School stays is_active=False, status='Pending'
            db.session.commit()
            
            # Show "Waiting for confirmation" page
            return render_template("onboarding/success.html", school_name=school.name)
        else:
            flash(f"Payment failed: {response}", "danger")
            
    return render_template("onboarding/payment.html", school=school)
