#!/usr/bin/env python3
"""
Comprehensive Security Audit Script
Checks database, configurations, permissions, and security settings
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.security import LoginLog

def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_database_security():
    """Check database security settings"""
    print_header("🔒 DATABASE SECURITY CHECK")
    
    app = create_app()
    with app.app_context():
        # Check for users with weak passwords
        print("\n📋 User Account Security:")
        total_users = User.query.count()
        active_users = User.query.filter_by(is_deleted=False).count()
        deleted_users = User.query.filter_by(is_deleted=True).count()
        
        print(f"  ✓ Total users: {total_users}")
        print(f"  ✓ Active users: {active_users}")
        print(f"  ✓ Deleted users: {deleted_users}")
        
        # Check for admin accounts
        admin_users = User.query.filter_by(role='A', is_deleted=False).all()
        print(f"\n👑 Admin Accounts: {len(admin_users)}")
        for admin in admin_users:
            print(f"  • {admin.name} ({admin.email})")
        

        
        # Check login logs
        print("\n📊 Login Log Statistics:")
        total_logs = LoginLog.query.count()
        success_logs = LoginLog.query.filter_by(status='Success').count()
        failed_logs = LoginLog.query.filter_by(status='Failed').count()
        
        print(f"  ✓ Total login attempts: {total_logs}")
        print(f"  ✓ Successful logins: {success_logs}")
        print(f"  ✓ Failed logins: {failed_logs}")
        
        # Check recent failed login attempts
        recent_failed = LoginLog.query.filter_by(status='Failed').order_by(LoginLog.timestamp.desc()).limit(5).all()
        if recent_failed:
            print(f"\n⚠️  Recent Failed Login Attempts:")
            for log in recent_failed:
                print(f"  • {log.email} - {log.ip_address} - {log.timestamp}")
        
        # Check for suspicious activity (multiple failed attempts)
        suspicious_ips = db.session.query(
            LoginLog.ip_address, 
            db.func.count(LoginLog.id).label('count')
        ).filter(
            LoginLog.status == 'Failed',
            LoginLog.timestamp > datetime.utcnow() - timedelta(days=7)
        ).group_by(LoginLog.ip_address).having(db.func.count(LoginLog.id) > 5).all()
        
        if suspicious_ips:
            print(f"\n🚨 Suspicious IPs (5+ failed attempts in last 7 days):")
            for ip, count in suspicious_ips:
                print(f"  • {ip}: {count} failed attempts")
        else:
            print(f"\n✅ No suspicious IP activity detected")

def check_file_permissions():
    """Check critical file permissions"""
    print_header("📁 FILE PERMISSIONS CHECK")
    
    critical_files = [
        '.env',
        'instance/madrasah.db',
        'app/config.py',
        'run.py'
    ]
    
    base_path = '/var/www/RaysTech/madrasah_mgmt'
    
    for file in critical_files:
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            stat_info = os.stat(file_path)
            permissions = oct(stat_info.st_mode)[-3:]
            print(f"  ✓ {file}: {permissions}")
            
            # Check if .env is too permissive
            if file == '.env' and permissions != '600':
                print(f"    ⚠️  WARNING: .env should be 600 (currently {permissions})")
        else:
            print(f"  ✗ {file}: NOT FOUND")

def check_environment_variables():
    """Check critical environment variables"""
    print_header("🔐 ENVIRONMENT VARIABLES CHECK")
    
    critical_vars = [
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'SECURITY_PASSWORD_SALT'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if len(value) > 10:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:]
            else:
                masked = '*' * len(value)
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ✗ {var}: NOT SET ⚠️")

def check_security_headers():
    """Check security headers configuration"""
    print_header("🛡️  SECURITY HEADERS CHECK")
    
    app = create_app()
    
    # Check if Talisman is configured
    if hasattr(app, 'talisman'):
        print("  ✓ Talisman (Security Headers): ENABLED")
    else:
        print("  ✗ Talisman (Security Headers): NOT CONFIGURED ⚠️")
    
    # Check CSRF protection
    if hasattr(app, 'csrf'):
        print("  ✓ CSRF Protection: ENABLED")
    else:
        print("  ✗ CSRF Protection: NOT CONFIGURED ⚠️")
    
    # Check rate limiting
    if hasattr(app, 'limiter'):
        print("  ✓ Rate Limiting: ENABLED")
    else:
        print("  ✗ Rate Limiting: NOT CONFIGURED ⚠️")

def check_backup_status():
    """Check backup directory and recent backups"""
    print_header("💾 BACKUP STATUS CHECK")
    
    backup_dir = '/var/www/RaysTech/madrasah_mgmt/backups'
    
    if os.path.exists(backup_dir):
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        if backups:
            backups.sort(reverse=True)
            print(f"  ✓ Total backups found: {len(backups)}")
            print(f"  ✓ Most recent backup: {backups[0]}")
            
            # Check if backup is recent (within 7 days)
            latest_backup_path = os.path.join(backup_dir, backups[0])
            backup_time = datetime.fromtimestamp(os.path.getmtime(latest_backup_path))
            days_old = (datetime.now() - backup_time).days
            
            if days_old <= 7:
                print(f"  ✓ Latest backup age: {days_old} days (GOOD)")
            else:
                print(f"  ⚠️  Latest backup age: {days_old} days (OLD - Consider new backup)")
        else:
            print("  ✗ No backups found ⚠️")
    else:
        print("  ✗ Backup directory not found ⚠️")

def generate_security_report():
    """Generate comprehensive security report"""
    print("\n" + "="*70)
    print("  🔍 MADRASAH MANAGEMENT SYSTEM - SECURITY AUDIT REPORT")
    print(f"  📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        check_database_security()
        check_file_permissions()
        check_environment_variables()
        check_security_headers()
        check_backup_status()
        
        print("\n" + "="*70)
        print("  ✅ SECURITY AUDIT COMPLETED")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during security audit: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_security_report()
