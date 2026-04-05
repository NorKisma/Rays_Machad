#!/usr/bin/env python3
"""
Auto-cleanup script for old login logs
Deletes login logs older than 60 days (2 months)
Run this script via cron job daily
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.security import LoginLog

def cleanup_old_logs(days=60):
    """
    Delete login logs older than specified days
    
    Args:
        days (int): Number of days to keep logs (default: 60 - 2 months)
    """
    app = create_app()
    
    with app.app_context():
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count logs to be deleted
        old_logs_count = LoginLog.query.filter(LoginLog.timestamp < cutoff_date).count()
        
        if old_logs_count == 0:
            print(f"✅ No logs older than {days} days found. Database is clean.")
            return
        
        # Delete old logs
        try:
            deleted = LoginLog.query.filter(LoginLog.timestamp < cutoff_date).delete()
            db.session.commit()
            
            print(f"✅ Successfully deleted {deleted} login logs older than {days} days")
            print(f"📅 Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show remaining logs count
            remaining = LoginLog.query.count()
            print(f"📊 Remaining logs in database: {remaining}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting logs: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    # Production mode: delete logs older than 60 days (2 months)
    cleanup_old_logs(days=60)


