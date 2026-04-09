import os
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # Execute raw SQL to create the intermediate table if it doesn't exist
    db.session.execute('''
    CREATE TABLE IF NOT EXISTS class_subjects (
        class_id INT NOT NULL,
        subject_id INT NOT NULL,
        PRIMARY KEY (class_id, subject_id),
        FOREIGN KEY (class_id) REFERENCES class_schedules(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    )
    ''')
    
    # Check if there are existing subjects that need moving
    res = db.session.execute('SELECT id, subject_id FROM class_schedules WHERE subject_id IS NOT NULL')
    records = res.fetchall()
    for row in records:
        class_id, subject_id = row
        try:
            db.session.execute('INSERT IGNORE INTO class_subjects (class_id, subject_id) VALUES (:class_id, :subject_id)', 
                {'class_id': class_id, 'subject_id': subject_id})
        except Exception as e:
            pass
            
    db.session.commit()
    print("Schema updated perfectly.")
