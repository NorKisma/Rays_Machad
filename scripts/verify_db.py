import os
import sys
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Fix for app factory expecting SQLALCHEMY_DATABASE_URI in env if missing
if os.environ.get('DATABASE_URL') and not os.environ.get('SQLALCHEMY_DATABASE_URI'):
    os.environ['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

from app import create_app, db

def verify_database_connection():
    app = create_app()
    with app.app_context():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"\n--- Database Configuration ---")
        # Mask password for security
        masked_url = db_url.replace(db_url.split(':')[2].split('@')[0], '******') if 'mysql' in db_url else db_url
        print(f"Database URL: {masked_url}")
        
        try:
            # Test connection
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT DATABASE();"))
                db_name = result.scalar()
                print(f"Connected to MySQL Database: {db_name}")
                
                # Check tables
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]
                print(f"\n--- Found {len(tables)} Tables ---")
                for table in tables:
                    # properly consuming the result proxy
                    count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    print(f"- {table}: {count} rows")
                    
                print("\n✅ SUCCESS: Connection verified to MySQL.")
                
        except Exception as e:
            print(f"\n❌ ERROR: Failed to connect to database.")
            print(e)
            sys.exit(1)

if __name__ == "__main__":
    verify_database_connection()
