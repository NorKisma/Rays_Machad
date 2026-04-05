import sys
import os

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.subject import Subject
from app.models.category import Category

app = create_app()

def seed_subjects():
    with app.app_context():
        # 1. Define Categories
        categories = [
            {'name': 'General', 'type': 'Subject', 'description': 'Mathematics, Science, and Academic subjects'},
            {'name': 'Islamic', 'type': 'Subject', 'description': 'Religious and Islamic studies'},
            {'name': 'Languages', 'type': 'Subject', 'description': 'Language and communication courses'}
        ]

        for cat_data in categories:
            cat = Category.query.filter_by(name=cat_data['name'], type=cat_data['type']).first()
            if not cat:
                cat = Category(**cat_data)
                db.session.add(cat)
                print(f"Added Category: {cat_data['name']}")
        db.session.commit()

        # 2. Define Subjects
        subjects = [
            # General
            {'name': 'Math', 'code': 'MATH', 'category': 'General', 'description': 'Mathematics'},
            {'name': 'Science', 'code': 'SCI', 'category': 'General', 'description': 'Science and Nature'},
            
            # Islamic
            {'name': 'Fiqhi', 'code': 'FIQ', 'category': 'Islamic', 'description': 'Islamic Jurisprudence'},
            {'name': 'Tawxiid', 'code': 'TAW', 'category': 'Islamic', 'description': 'Oneness of Allah'},
            {'name': 'Akhlaaq', 'code': 'AKH', 'category': 'Islamic', 'description': 'Islamic Ethics and Manners'},
            {'name': 'Taariikh Islaami', 'code': 'TAI', 'category': 'Islamic', 'description': 'Islamic History'},
            
            # Languages
            {'name': 'Somali', 'code': 'SOM', 'category': 'Languages', 'description': 'Somali Language'},
            {'name': 'English', 'code': 'ENG', 'category': 'Languages', 'description': 'English Language'},
            {'name': 'Carabi', 'code': 'ARB', 'category': 'Languages', 'description': 'Arabic Language'}
        ]

        for subj_data in subjects:
            subj = Subject.query.filter_by(code=subj_data['code']).first()
            if not subj:
                subj = Subject(**subj_data)
                db.session.add(subj)
                print(f"Added Subject: {subj_data['name']}")
            else:
                # Update existing if needed
                subj.name = subj_data['name']
                subj.category = subj_data['category']
                subj.description = subj_data['description']
                print(f"Updated Subject: {subj_data['name']}")
        
        db.session.commit()
        
        # 3. Update System Settings
        from app.models.setting import SystemSetting
        SystemSetting.set_setting('madrasah_name', 'Machadka Rays (Rays Academy)', 'The name of the institution')
        SystemSetting.set_setting('active_term', 'Term One 2026', 'Current academic term')
        
        print("Subject seeding and settings update completed!")

if __name__ == "__main__":
    seed_subjects()
