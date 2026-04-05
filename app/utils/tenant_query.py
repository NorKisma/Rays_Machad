from flask_sqlalchemy.query import Query
from flask import has_request_context
from sqlalchemy import event

class TenantQuery(Query):
    """
    A custom query class that facilitates filtering by school_id.
    """
    def filter_by_tenant(self):
        if has_request_context():
            from app.utils.tenant_context import get_current_school
            school = get_current_school()
            if school:
                # Check if the model being queried has school_id attribute
                try:
                    # SQLAlchemy 1.4/2.0 compatible way to get the primary model
                    model = self._propagate_attrs.get("plugin_subject")
                    if not model and len(self.column_descriptions) > 0:
                        model = self.column_descriptions[0]['entity']
                    
                    if model and hasattr(model, 'school_id'):
                        return self.filter_by(school_id=school.id)
                except Exception:
                    pass
        return self

@event.listens_for(Query, "before_compile", retval=True)
def before_compile(query):
    """
    Automatically applies tenant filtering to any query that involves a model 
    with a 'school_id' attribute, unless it's the 'School' model itself.
    """
    if not has_request_context():
        return query

    # Skip if it's already filtered or if we are the SaaS Super Admin
    # Note: We can add more complex logic here if needed.
    
    from app.utils.tenant_context import get_current_school
    school = get_current_school()
    if not school:
        return query

    # Check if the model has school_id
    try:
        model = query._propagate_attrs.get("plugin_subject")
        if not model and len(query.column_descriptions) > 0:
            model = query.column_descriptions[0]['entity']
        
        from app.models.school import School
        if model and model != School and hasattr(model, 'school_id'):
            # Only apply if not already filtered by school_id
            # This is a bit tricky to detect, but SQLAlchemy's filter is additive anyway.
            return query.filter_by(school_id=school.id)
    except Exception:
        pass

    return query
