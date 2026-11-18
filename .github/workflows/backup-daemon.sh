#!/bin/bash
set -u
BACKUP_PASS="${BACKUP_PASS:?}"
REMOTE="your-remote"
REMOTE_PATH="backups/actions"
INTERVAL=60
COLLECT_DIR="/tmp/collect"
WORK="/home/runner/work"
mkdir -p "$COLLECT_DIR"
cleanup() { rm -rf "$COLLECT_DIR"/* /tmp/session-backup.tar.gz /tmp/session-backup.enc; }
trap cleanup EXIT
while true; do
  rsync -a --delete --include='*/' --include='*.py' --include='*.json' --include='*.txt' --include='*.csv' --include='*.log' --include='*.db' --include='*.pkl' --include='*.cookies' --exclude='*' "$WORK/" "$COLLECT_DIR/" 2>/dev/null
  if [ -z "$(ls -A "$COLLECT_DIR")" ]; then sleep "$INTERVAL"; continue; fi
  tar -czf /tmp/session-backup.tar.gz -C "$COLLECT_DIR" . 2>/dev/null || { sleep "$INTERVAL"; continue; }
  openssl enc -aes-256-cbc -pbkdf2 -salt -in /tmp/session-backup.tar.gz -out /tmp/session-backup.enc -pass pass:"$BACKUP_PASS" 2>/dev/null || { sleep "$INTERVAL"; continue; }
  STAMP=$(date +%Y%m%d-%H%M%S)-$RANDOM
  rclone copy /tmp/session-backup.enc "$REMOTE:$REMOTE_PATH/session-$STAMP.enc" --no-traverse --quiet 2>/dev/null
  rm -f /tmp/session-backup.tar.gz /tmp/session-backup.enc
  sleep "$INTERVAL"
done