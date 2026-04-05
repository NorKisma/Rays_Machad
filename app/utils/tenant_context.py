from flask import g, request, current_app
from app.models.school import School

def get_current_school():
    """
    Returns the school object based on the current subdomain or domain.
    Caches the result in flask.g for the duration of the request.
    """
    if 'current_school' not in g:
        host = request.host.split(':')[0]
        
        # Helper to check if string is an IP address
        def is_ip(h):
            p = h.split('.')
            return len(p) == 4 and all(i.isdigit() for i in p)
            
        g.current_school = None
        
        if not is_ip(host) and host not in ['localhost', '127.0.0.1']:
            parts = host.split('.')
            # If we have school.raystechcenter.online, school is parts[0]
            if len(parts) >= 3:
                subdomain = parts[0]
                g.current_school = School.get_by_subdomain(subdomain)
            else:
                # Check for custom domain mapping
                g.current_school = School.query.filter_by(domain=host, is_active=True).first()
            
    return g.current_school

def tenant_filter(model):
    """
    Utility to filter a query by the current school.
    Usage: students = tenant_filter(Student).all()
    """
    school = get_current_school()
    if school:
        return model.query.filter_by(school_id=school.id)
    return model.query
