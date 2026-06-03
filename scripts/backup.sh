#!/bin/bash
# SecureApp Database Backup Script
# Scheduled via cron: 0 2 * * * /home/ubuntu/cloud-secure-web-app/scripts/backup.sh

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/secureapp_backups"
LOG_FILE="/var/log/secureapp_backup.log"
S3_BUCKET="secureapp-backups-pranav"
RDS_HOST="secureapp-db.c34iggw2e8lx.ap-south-1.rds.amazonaws.com"
RDS_USER="admin"
RDS_PASS="SecureApp2026"
RDS_DB="secureapp"

mkdir -p "$BACKUP_DIR"
echo "[$(date)] Starting backup..." | tee -a "$LOG_FILE"

# Dump MySQL database
DUMP_FILE="$BACKUP_DIR/secureapp_mysql_${TIMESTAMP}.sql.gz"
mysqldump -h "$RDS_HOST" \
          -u "$RDS_USER" \
          -p"$RDS_PASS" \
          "$RDS_DB" | gzip > "$DUMP_FILE"
echo "[$(date)] MySQL dump created: $DUMP_FILE" | tee -a "$LOG_FILE"

# Upload to S3
aws s3 cp "$DUMP_FILE" \
    "s3://${S3_BUCKET}/backups/" \
    --region ap-south-1
echo "[$(date)] Uploaded to S3" | tee -a "$LOG_FILE"

# Cleanup local files older than 7 days
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete

echo "[$(date)] Backup complete." | tee -a "$LOG_FILE"