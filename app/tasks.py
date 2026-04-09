from .extensions import celery, db
from .models.user import User
from .models.school import School
from datetime import datetime, timedelta
from flask import current_app

@celery.task
def cleanup_deleted_entities():
    """
    Permanently delete users and schools who have been soft-deleted for more than 60 days.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=60)
    
    # 1. Cleanup Users
    users_to_purge = User.query.filter(User.deleted_at <= cutoff_date).all()
    user_count = 0
    for user in users_to_purge:
        current_app.logger.info(f"PERMANENT CLEANUP: Deleting user {user.email} (Soft-deleted on {user.deleted_at})")
        db.session.delete(user)
        user_count += 1
    
    # 2. Cleanup Schools
    schools_to_purge = School.query.filter(School.deleted_at <= cutoff_date).all()
    school_count = 0
    for school in schools_to_purge:
        current_app.logger.info(f"PERMANENT CLEANUP: Deleting school {school.subdomain} (Soft-deleted on {school.deleted_at})")
        
        # Optionally, drop the physical database if you want to be very thorough
        # db_name = f"rays_machad_tenant_{school.subdomain}"
        # db.session.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        
        db.session.delete(school)
        school_count += 1
    
    if user_count > 0 or school_count > 0:
        db.session.commit()
    
    return f"Cleanup complete. Purged {user_count} users and {school_count} schools deleted over 60 days ago."
