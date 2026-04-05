from app.extensions import db
from app.models.mixins import SchoolContextMixin

class RolePermission(db.Model, SchoolContextMixin):
    __tablename__ = 'role_permissions'
    __table_args__ = {'schema': 'madrasah_db'}
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10), nullable=False) # 'A', 'T', 'S', 'F', 'P', 'U'
    module = db.Column(db.String(50), nullable=False) # 'students', 'teachers', 'classes', etc.
    is_allowed = db.Column(db.Boolean, default=False)

    @staticmethod
    def check(role, module):
        # Admin always has access to everything
        if role in ['A', 'Admin']:
            return True
            
        from app.utils.tenant_context import get_current_school
        school = get_current_school()
        school_id = school.id if school else None
            
        perm = RolePermission.query.filter_by(role=role, module=module, school_id=school_id).first()
        
        # If no school-specific permission, check global default (where school_id is None)
        if not perm and school_id is not None:
             perm = RolePermission.query.filter_by(role=role, module=module, school_id=None).first()
        
        # Default behavior if no permission record exists
        if not perm:
            return False
            
        return perm.is_allowed

    @staticmethod
    def set_permission(role, module, is_allowed):
        from app.utils.tenant_context import get_current_school
        school = get_current_school()
        school_id = school.id if school else None
        RolePermission.set_permission_for_school(role, module, is_allowed, school_id)

    @staticmethod
    def set_permission_for_school(role, module, is_allowed, school_id):
        perm = RolePermission.query.filter_by(role=role, module=module, school_id=school_id).first()
        if perm:
            perm.is_allowed = is_allowed
        else:
            perm = RolePermission(role=role, module=module, is_allowed=is_allowed, school_id=school_id)
            db.session.add(perm)
        db.session.commit()
