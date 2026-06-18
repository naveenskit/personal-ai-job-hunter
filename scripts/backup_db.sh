#!/usr/bin/env bash
set -euo pipefail

# Simple Postgres backup using pg_dump; expects DATABASE_URL env var
if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is not set"
  exit 1
fi

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
OUTDIR=${BACKUP_DIR:-./backups}
mkdir -p "$OUTDIR"

FILENAME="$OUTDIR/db_backup_$TIMESTAMP.sql.gz"

echo "Dumping database to $FILENAME"
pg_dump "$DATABASE_URL" | gzip > "$FILENAME"

echo "Backup saved: $FILENAME"
