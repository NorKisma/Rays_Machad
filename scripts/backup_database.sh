#!/bin/bash
# Database Backup Script
# Creates timestamped backup of the database

BACKUP_DIR="/var/www/RaysTech/rays_machad_mgmt/backups"
DB_NAME="Rays_machda"
DB_USER="rays_machad_admin"
DB_PASS="RaysTech2026"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "🔄 Creating database backup..."
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "✅ Backup created successfully: ${BACKUP_FILE}.gz"
    
    # Keep only last 7 backups
    cd "$BACKUP_DIR"
    ls -t ${DB_NAME}_*.sql.gz | tail -n +8 | xargs -r rm
    echo "📦 Old backups cleaned up (keeping last 7)"
else
    echo "❌ Backup failed!"
    exit 1
fi
