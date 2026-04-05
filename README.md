Rays Academy (Machadka Rays) Management System

A full-featured Education Management System for Rays Academy, built with Python Flask, MySQL, and AI-powered automation. This platform supports a combined curriculum of Modern and Islamic subjects, managing students, teachers, classes, attendance, exams, and fees.

Table of Contents

Features

Tech Stack

Folder Structure

Installation

Configuration

Usage

AI Automation

Testing



Features
Student Management – Add, update, and manage student records
Teacher Management – Manage teacher profiles and schedules
Class Scheduling – Create, view, and assign classes
Attendance Tracking – Track student attendance, AI-assisted
Exams & Grading – Manage exams, grades, and reports
Fee Management – Track payments and generate invoices
AI Automation – Automate attendance, grading, and notifications
User Authentication – Secure login for admin, teachers, and students
Tech Stack
Backend: Python Flask, Flask Blueprints
Database: MySQL with SQLAlchemy ORM
Frontend: HTML, CSS, JavaScript (Bootstrap optional)
AI Automation: Python AI modules (attendance bot, grading bot, notification bot)
Extensions: Flask-Migrate, Flask-Login, Flask-WTF

Madrasah Management System – Folder Structure
madrasah_management/
│
├── app/
│   ├── __init__.py                 # Initialize Flask app, DB, and Blueprints
│   ├── config.py                   # Configuration (DB, AI keys, env)
│   ├── extensions.py               # Initialize extensions (SQLAlchemy, Migrate, Login, etc.)
│   ├── models/                     # Database models
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── teacher.py
│   │   ├── class_schedule.py
│   │   ├── attendance.py
│   │   ├── exam.py
│   │   └── fee.py
│   │
│   ├── blueprints/                 # Modular Flask Blueprints
│   │   ├── __init__.py
│   │   ├── auth/                   # Authentication & Authorization
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── templates/
│   │   ├── students/
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── templates/
│   │   ├── teachers/
│   │   │   ├── routes.py
│   │   │   ├── forms.py
│   │   │   └── templates/
│   │   ├── classes/
│   │   │   ├── routes.py
│   │   │   └── templates/
│   │   ├── attendance/
│   │   │   ├── routes.py
│   │   │   └── templates/
│   │   └── exams/
│   │       ├── routes.py
│   │       └── templates/
│   │
│   ├── ai_automation/             # AI-powered automation features
│   │   ├── __init__.py
│   │   ├── attendance_bot.py       # AI-driven attendance tracking
│   │   ├── grading_bot.py          # AI-based grading & reports
│   │   └── notification_bot.py    # AI notifications & reminders
│   │
│   ├── templates/                  # Global templates
│   │   ├── base.html
│   │   └── layout.html
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       ├── images/
│       └── uploads/                # For student profile images, docs, etc.
│
├── migrations/                     # DB migrations (Flask-Migrate)
│
├── tests/                           # Unit and integration tests
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_students.py
│   └── test_teachers.py
│
├── requirements.txt                # Python dependencies
├── run.py                           # App entry point
├── .env                             # Environment variables (DB credentials, AI API keys)
└── README.md                        # Project documentation



Installation
Clone the repository
git clone https://github.com/yourusername/madrasah_management.git
cd madrasah_management
Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows


Install dependencies
pip install -r requirements.txt

Set up the database
CREATE DATABASE madrasah_db;

Configure environment variables
Create a .env file:
SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://user:password@localhost/madrasah_db
AI_API_KEY=your_ai_key


Run migrations
flask db init
flask db migrate
flask db upgrade

Usage
Run the application
python run.py

Access the app
Open your browser at http://127.0.0.1:5000/
Login
Admin: Full access
Teachers: Manage classes, attendance, grades
Students: View classes, attendance, and exam results
AI Automation
Attendance Bot → Uses AI for automatic attendance tracking
Grading Bot → Auto-grades exams and generates reports
Notification Bot → Sends reminders to students, parents, or teachers
All AI modules are located in app/ai_automation/ and are modular for easy scaling.

Testing
Run tests using pytest:
pytest tests/
Test coverage includes authentication, student management, teacher management, and AI automation modules.