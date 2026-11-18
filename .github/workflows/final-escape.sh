#!/bin/bash
set -u
BACKUP_PASS="${BACKUP_PASS:-}"
[ -z "$BACKUP_PASS" ] && exit 0
tar -czf /tmp/final.tar.gz -C /home/runner/work . 2>/dev/null || exit 0
openssl enc -aes-256-cbc -pbkdf2 -salt -in /tmp/final.tar.gz -out /tmp/final.enc -pass pass:"$BACKUP_PASS" 2>/dev/null || exit 0
STAMP=$(date +%Y%m%d-%H%M%S)-$RANDOM
rclone copy /tmp/final.enc "your-remote:backups/actions/final/final-$STAMP.enc" --no-traverse --quiet 2>/dev/null
rm -f /tmp/final.tar.gz /tmp/final.enc