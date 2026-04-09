from app.extensions import db

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    __table_args__ = {'schema': 'Rays_machda'}
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('Rays_machda.schools.id'), nullable=True)
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))

    @staticmethod
    def get_setting(key, default=None):
        from app.utils.tenant_context import get_current_school
        school = get_current_school()
        
        # Try to find school-specific setting first
        if school:
            setting = SystemSetting.query.filter_by(key=key, school_id=school.id).first()
            if setting:
                return setting.value
        
        # Fallback to global setting
        global_setting = SystemSetting.query.filter_by(key=key, school_id=None).first()
        return global_setting.value if global_setting else default

    @staticmethod
    def set_setting(key, value, description=None, school_id=None):
        if school_id is None:
            from flask import has_request_context
            if has_request_context():
                from app.utils.tenant_context import get_current_school
                school = get_current_school()
                school_id = school.id if school else None
            else:
                school_id = None
        
        setting = SystemSetting.query.filter_by(key=key, school_id=school_id).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SystemSetting(key=key, value=value, description=description, school_id=school_id)
            db.session.add(setting)
        db.session.commit()
