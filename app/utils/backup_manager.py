import os
import shutil
import subprocess
from datetime import datetime
from flask import current_app

def perform_system_backup():
    """
    Performs a backup of the current database (SQLite or MySQL).
    Saves the backup file in the 'backups' directory at the project root.
    """
    # Create backups directory in the root folder
    root_dir = os.path.abspath(os.path.join(current_app.root_path, '..'))
    backup_dir = os.path.join(root_dir, 'backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    try:
        if 'sqlite' in db_uri:
            # Handle SQLite
            db_filename = db_uri.replace('sqlite:///', '')
            if not os.path.isabs(db_filename):
                # Usually in instance folder
                db_path = os.path.join(current_app.instance_path, db_filename)
            else:
                db_path = db_filename
                
            backup_filename = f'backup_{timestamp}.sqlite.db'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(db_path, backup_path)
            return True, backup_filename
            
        elif 'mysql' in db_uri:
            # Handle MySQL using mysqldump
            # URI Format: mysql+pymysql://user:pass@host:port/dbname
            import re
            parts = re.search(r'mysql(?:\+pymysql)?://(?P<user>[^:]+)(?::(?P<password>[^@]+))?@(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<db>.+)', db_uri)
            
            if not parts:
                return False, "Could not parse MySQL connection string."
                
            user = parts.group('user')
            password = parts.group('password')
            host = parts.group('host')
            port = parts.group('port') or '3306'
            db_name = parts.group('db')
            
            backup_filename = f'backup_{timestamp}.mysql.sql'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Find mysqldump executable
            mysqldump_path = current_app.config.get('MYSQLDUMP_PATH')
            if not mysqldump_path:
                mysqldump_path = shutil.which('mysqldump')
            
            # Fallback to common Linux path if still not found
            if not mysqldump_path:
                for common_path in ['/usr/bin/mysqldump', '/usr/local/bin/mysqldump']:
                    if os.path.exists(common_path):
                        mysqldump_path = common_path
                        break
            
            if not mysqldump_path or not os.path.exists(mysqldump_path):
                return False, "Could not find 'mysqldump' executable. Please ensure MySQL Client is installed."
            
            # Construct command
            # Using --result-file to handle spaces in paths if any
            cmd = [mysqldump_path, f'--user={user}', f'--host={host}', f'--port={port}']
            if password:
                cmd.append(f'--password={password}')
            cmd.extend(['--result-file=' + backup_path, db_name])
            
            # Use shell=False for security, but ensure the path is absolute
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, backup_filename
            else:
                return False, f"MySQL Dump Error: {result.stderr}"
        
        return False, "Unsupported database type for backup."
    except Exception as e:
        return False, str(e)

def get_backup_list():
    """Returns a list of available backups."""
    root_dir = os.path.abspath(os.path.join(current_app.root_path, '..'))
    backup_dir = os.path.join(root_dir, 'backups')
    
    if not os.path.exists(backup_dir):
        return []
        
    backups = []
    for f in os.listdir(backup_dir):
        if f.startswith('backup_'):
            path = os.path.join(backup_dir, f)
            stats = os.stat(path)
            backups.append({
                'filename': f,
                'size': f"{stats.st_size / 1024:.2f} KB",
                'date': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sort by date descending
    backups.sort(key=lambda x: x['date'], reverse=True)
    return backups

def send_backup_to_email(filename):
    """Sends the specified backup file to the configured madrasah email."""
    from flask_mail import Message
    from app.extensions import mail
    from app.models.setting import SystemSetting
    
    root_dir = os.path.abspath(os.path.join(current_app.root_path, '..'))
    file_path = os.path.join(root_dir, 'backups', filename)
    
    if not os.path.exists(file_path):
        return False, "Backup file not found."
        
    # Get the recipient email from settings (Madrasah Email preferred)
    recipient_email = SystemSetting.get_setting('madrasah_email')
    if not recipient_email:
        recipient_email = SystemSetting.get_setting('admin_email', current_app.config.get('MAIL_USERNAME'))
        
    madrasah_name = SystemSetting.get_setting('madrasah_name', 'Madrasah System')
    
    if not recipient_email:
        return False, "No administrator or madrasah email configured."
        
    try:
        subject = f"System Backup: {madrasah_name} ({datetime.now().strftime('%Y-%m-%d')})"
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        
        # Construct restore instructions in Somali and English
        restore_instructions = f"""
----------------------------------------------------------
HAGAHA SOO CELINTA (RESTORE INSTRUCTIONS)
----------------------------------------------------------

Sidee loo soo celiyaa xogtan (How to restore this backup):

1. HADDII AY TAHAY MySQL (.sql file):
   - Isticmaal amarka printer-ka (terminal):
     mysql -u [username] -p [database_name] < {filename}
   - Tusaale: mysql -u madrasah_admin -p madrasah_db < {filename}

2. HADDII AY TAHAY SQLite (.db file):
   - Kaga bedel faylka 'madrasah.db' ee ku dhex jira folder-ka 'instance/' midka cusub ee aad haysato.

FIIRO GAAR AH: Hubi inaad haysato nuqul (backup) ka hor inta aadan samayn restore.
----------------------------------------------------------
"""

        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[recipient_email]
        )
        msg.body = f"Attached is the database backup for {madrasah_name}.\nGenerated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nFilename: {filename}\n\n{restore_instructions}"
        
        with open(file_path, 'rb') as fp:
            msg.attach(filename, "application/octet-stream", fp.read())
            
        mail.send(msg)
        return True, f"Backup sent to {recipient_email}"
    except Exception as e:
        return False, f"Email Error: {str(e)}"

def restore_database_from_file(file_path):
    """
    Restores the database from a given SQL (MySQL) or DB (SQLite) file.
    """
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    try:
        if 'sqlite' in db_uri:
            # Handle SQLite Restore
            db_filename = db_uri.replace('sqlite:///', '')
            if not os.path.isabs(db_filename):
                db_path = os.path.join(current_app.instance_path, db_filename)
            else:
                db_path = db_filename
            
            # Close existing connections before overriding (standard practice)
            from app.extensions import db
            db.session.remove()
            db.engine.dispose()
            
            shutil.copy2(file_path, db_path)
            return True, "SQLite database restored successfully."
            
        elif 'mysql' in db_uri:
            # Handle MySQL Restore
            import re
            parts = re.search(r'mysql(?:\+pymysql)?://(?P<user>[^:]+)(?::(?P<password>[^@]+))?@(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<db>.+)', db_uri)
            
            if not parts:
                return False, "Could not parse MySQL connection string."
                
            user = parts.group('user')
            password = parts.group('password')
            host = parts.group('host')
            port = parts.group('port') or '3306'
            db_name = parts.group('db')
            
            # Find mysql executable (not mysqldump for restore)
            mysql_path = shutil.which('mysql')
            if not mysql_path:
                for cp in ['/usr/bin/mysql', '/usr/local/bin/mysql']:
                    if os.path.exists(cp):
                        mysql_path = cp
                        break
            
            if not mysql_path:
                return False, "MySQL client not found. Please install MySQL client."
            
            # Construct command
            cmd = [mysql_path, f'--user={user}', f'--host={host}', f'--port={port}']
            if password:
                cmd.append(f'--password={password}')
            cmd.append(db_name)
            
            # Run restore from stdin
            with open(file_path, 'r') as f:
                result = subprocess.run(cmd, stdin=f, capture_output=True, text=True)
                
            if result.returncode == 0:
                return True, "MySQL database restored successfully."
            else:
                return False, f"MySQL Restore Error: {result.stderr}"
                
        return False, "Unsupported database type for restore."
    except Exception as e:
        return False, str(e)
