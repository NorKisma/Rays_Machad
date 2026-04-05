import random
import string
from datetime import datetime

def generate_student_id():
    """Generates a unique student enrollment number."""
    from app.models.student import Student
    year = datetime.utcnow().year
    
    # Try to find the last student to increment the number
    last_student = Student.query.order_by(Student.id.desc()).first()
    
    if not last_student:
        return f"STD-{year}-001"
    
    try:
        last_id = last_student.enrollment_number
        if "-" in last_id:
            parts = last_id.split("-")
            # If the last part is a number, increment it
            if parts[-1].isdigit():
                num = int(parts[-1])
                return f"{'-'.join(parts[:-1])}-{str(num + 1).zfill(3)}"
    except Exception:
        pass
        
    return f"STD-{year}-{str(last_student.id + 1).zfill(3)}"

def generate_teacher_id():
    """Generates a unique teacher employee number."""
    from app.models.teacher import Teacher
    year = datetime.utcnow().year
    
    last_teacher = Teacher.query.order_by(Teacher.id.desc()).first()
    
    if not last_teacher:
        return f"TEA-{year}-001"
    
    try:
        last_id = last_teacher.employee_number
        if "-" in last_id:
            parts = last_id.split("-")
            if parts[-1].isdigit():
                num = int(parts[-1])
                return f"{'-'.join(parts[:-1])}-{str(num + 1).zfill(3)}"
    except Exception:
        pass
        
    return f"TEA-{year}-{str(last_teacher.id + 1).zfill(3)}"

def generate_transaction_id(prefix="TRX"):
    """Generates a random unique transaction ID."""
    chars = string.ascii_uppercase + string.digits
    unique_str = ''.join(random.choice(chars) for _ in range(8))
    return f"{prefix}-{unique_str}"
