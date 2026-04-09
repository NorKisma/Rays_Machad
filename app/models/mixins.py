from flask import g, has_request_context
from app.extensions import db
from app.utils.tenant_query import TenantQuery
from sqlalchemy import event

class SchoolContextMixin:
    """
    A mixin to add school_id and a relationship to School for multi-tenancy.
    """
    school_id = db.Column(db.Integer, db.ForeignKey('Rays_machda.schools.id'), nullable=True, index=True)
    
    @classmethod
    def tenant_query(cls):
        """
        The main way to fetch data for the current school.
        Usage: Student.tenant_query().all()
        """
        return cls.query.filter_by_tenant()

@event.listens_for(db.Session, "before_flush")
def before_flush(session, flush_context, instances):
    """
    Automatically sets the school_id for any new object that inherits from SchoolContextMixin.
    """
    if has_request_context():
        from app.utils.tenant_context import get_current_school
        school = get_current_school()
        
        if school:
            for obj in session.new:
                if isinstance(obj, SchoolContextMixin):
                    if obj.school_id is None:
                        obj.school_id = school.id
