from flask_babel import gettext as _

def get_message_templates():
    """
    Returns a dictionary of message templates for Parents and Teachers.
    Placeholders like {student_name} are used for dynamic content.
    """
    return {
        # ==========================================
        # PARENT TEMPLATES
        # ==========================================
        'parent': {
            'attendance_absent': _("Assalamu Alaykum {parent_name}, your child {student_name} was marked ABSENT today ({date}). Please contact us if this is an error."),
            
            'attendance_late': _("Assalamu Alaykum {parent_name}, your child {student_name} arrived LATE to class today at {time}."),
            
            'fee_due_reminder': _("Reminder: School fees for {student_name} ({amount}) are due by {due_date}. Please clear the balance to avoid interruption."),
            
            'fee_received': _("Jazak'Allah Khair. We have received payment of {amount} for {student_name}. Remaining balance: {balance}."),
            
            'exam_result': _("Exam Alert: {student_name} scored {score}% in {subject}. Grade: {grade}."),
            
            'monthly_report': _("Monthly Report for {month}: {student_name} has {attendance}% attendance and is currently on {current_lesson}. See details: {link}"),
            
            'holiday_announcement': _("Announcement: The Rays Machad will be closed from {start_date} to {end_date} for {occasion}. Classes resume on {resume_date}."),
            
            'general_meeting': _("Invitation: Dear Parents, please join us for a parent-teacher meeting on {date} at {time} to discuss student progress."),
        },

        # ==========================================
        # TEACHER TEMPLATES
        # ==========================================
        'teacher': {
            'class_reminder': _("Ustadh {teacher_name}, you have a class: {subject} with {class_name} at {time} in Room {room}."),
            
            'schedule_change': _("Update: Your class schedule for {date} has changed. Please check the dashboard for details."),
            
            'salary_processed': _("Your salary for the month of {month} has been processed and sent to your account."),
            
            'staff_meeting': _("Staff Meeting Alert: Please attend the mandatory staff meeting on {date} at {time} in the main hall."),
            
            'leave_approved': _("Your leave request for {dates} has been APPROVED."),
            
            'leave_rejected': _("Your leave request for {dates} has been DENIED. Please contact administration."),
        }
    }

def format_message(category, template_key, **kwargs):
    """
    Retreive and format a message template.
    
    Usage:
    msg = format_message('parent', 'attendance_absent', parent_name="Ali", student_name="Ahmed", date="2024-02-07")
    """
    templates = get_message_templates()
    
    if category not in templates:
        return f"Error: Category '{category}' not found."
        
    if template_key not in templates[category]:
        return f"Error: Template '{template_key}' not found."
        
    template_str = templates[category][template_key]
    
    try:
        return template_str.format(**kwargs)
    except KeyError as e:
        return f"Error: Missing data for placeholder {str(e)}"
