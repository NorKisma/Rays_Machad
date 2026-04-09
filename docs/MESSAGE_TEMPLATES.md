# Message Templates

This document lists the available message templates for Parents and Teachers in the Rays Machad Management System. These can be used with the `MessagingService` to send notifications via SMS or WhatsApp.

## 👥 Parent Templates

| Key | Template Text | Placeholders |
| --- | --- | --- |
| `attendance_absent` | Assalamu Alaykum {parent_name}, your child {student_name} was marked ABSENT today ({date}). Please contact us if this is an error. | `parent_name`, `student_name`, `date` |
| `attendance_late` | Assalamu Alaykum {parent_name}, your child {student_name} arrived LATE to class today at {time}. | `parent_name`, `student_name`, `time` |
| `fee_due_reminder` | Reminder: School fees for {student_name} ({amount}) are due by {due_date}. Please clear the balance to avoid interruption. | `student_name`, `amount`, `due_date` |
| `fee_received` | Jazak'Allah Khair. We have received payment of {amount} for {student_name}. Remaining balance: {balance}. | `amount`, `student_name`, `balance` |
| `exam_result` | Exam Alert: {student_name} scored {score}% in {subject}. Grade: {grade}. | `student_name`, `score`, `subject`, `grade` |
| `monthly_report` | Monthly Report for {month}: {student_name} has {attendance}% attendance and is currently on {current_lesson}. See details: {link} | `month`, `student_name`, `attendance`, `current_lesson`, `link` |
| `holiday_announcement` | Announcement: The Rays Machad will be closed from {start_date} to {end_date} for {occasion}. Classes resume on {resume_date}. | `start_date`, `end_date`, `occasion`, `resume_date` |
| `general_meeting` | Invitation: Dear Parents, please join us for a parent-teacher meeting on {date} at {time} to discuss student progress. | `date`, `time` |

## 👨‍🏫 Teacher Templates

| Key | Template Text | Placeholders |
| --- | --- | --- |
| `class_reminder` | Ustadh {teacher_name}, you have a class: {subject} with {class_name} at {time} in Room {room}. | `teacher_name`, `subject`, `class_name`, `time`, `room` |
| `schedule_change` | Update: Your class schedule for {date} has changed. Please check the dashboard for details. | `date` |
| `salary_processed` | Your salary for the month of {month} has been processed and sent to your account. | `month` |
| `staff_meeting` | Staff Meeting Alert: Please attend the mandatory staff meeting on {date} at {time} in the main hall. | `date`, `time` |
| `leave_approved` | Your leave request for {dates} has been APPROVED. | `dates` |
| `leave_rejected` | Your leave request for {dates} has been DENIED. Please contact administration. | `dates` |

## 💻 Usage in Code

You can use the helper function `format_message` in `app/utils/message_templates.py`:

```python
from app.utils.message_templates import format_message
from app.utils.messaging import MessagingService

# 1. Format the message
msg = format_message('parent', 'attendance_absent', 
    parent_name="Ali", 
    student_name="Ahmed", 
    date="2024-02-07"
)

# 2. Send it
ms = MessagingService()
ms.send_hybrid_message("+252615000000", msg)
```
