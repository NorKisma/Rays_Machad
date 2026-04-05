import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.permission import RolePermission

def seed_permissions():
    app = create_app()
    with app.app_context():
        # Define roles and modules
        roles = ['T', 'S', 'F', 'P']
        modules = ['students', 'teachers', 'classes', 'attendance', 'exams', 'financials', 'reports', 'manage_users']
        
        # Default Permissions
        # (Role, Module, IsAllowed)
        defaults = [
            # Teacher
            ('T', 'students', True),
            ('T', 'teachers', True),
            ('T', 'classes', True),
            ('T', 'attendance', True),
            ('T', 'exams', True),
            
            # Staff
            ('S', 'students', True),
            ('S', 'teachers', True),
            ('S', 'classes', True),
            ('S', 'attendance', True),
            ('S', 'exams', True),
            ('S', 'financials', True),
            ('S', 'reports', True),
            ('S', 'manage_users', True),
            
            # Finance
            ('F', 'students', True),
            ('F', 'teachers', True),
            ('F', 'classes', True),
            ('F', 'attendance', True),
            ('F', 'exams', True),
            ('F', 'financials', True),
            ('F', 'reports', True),
            ('F', 'manage_users', True),
            
            # Parent
            ('P', 'students', True),
            ('P', 'classes', True),
            ('P', 'attendance', True),
            ('P', 'exams', True),
            ('P', 'financials', True),
            ('P', 'reports', True),
        ]
        
        print("Seeding permissions...")
        for role, module, is_allowed in defaults:
            RolePermission.set_permission(role, module, is_allowed)
        
        # Ensure all role-module combinations exist (defaulting to False if not in defaults)
        for r in roles:
            for m in modules:
                perm = RolePermission.query.filter_by(role=r, module=m).first()
                if not perm:
                    RolePermission.set_permission(r, m, False)
                    
        print("Done!")

if __name__ == '__main__':
    seed_permissions()
