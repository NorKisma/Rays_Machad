import sqlite3
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'instance', 'rays_machad.db')

if not os.path.exists(db_path):
    print(f"File {db_path} does not exist.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    # Check students if table exists
    if ('students',) in tables:
        cursor.execute("SELECT id, full_name, status FROM students WHERE status='Active'")
        students = cursor.fetchall()
        print(f"\nActive Students in SQLite ({len(students)}):")
        for s in students:
            print(s)
    else:
        print("No 'students' table found.")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
