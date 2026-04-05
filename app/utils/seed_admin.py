from app import create_app   # import your Flask app factory
from app.models import User
from app.extensions import db
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

admin_email = "nor.jws@gmail.com"

def create_first_admin():
    app = create_app()  # or import your existing app
    with app.app_context():  # <-- important
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin = User(
                name="Rays Tech Center",
                email=admin_email,
                password_hash=generate_password_hash("Rays2026"),
                role="Admin",
                is_active=True
            )
            try:
                db.session.add(admin)
                db.session.commit()
                print("First admin created successfully")
            except IntegrityError:
                db.session.rollback()
                print("Admin already exists, skipping creation")
        else:
            print("Admin already exists, skipping creation")
