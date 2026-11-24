# DukaanDost AI - Backup & Disaster Recovery Guide

## 1. Disaster Recovery Objectives

- **Recovery Point Objective (RPO):** < 1 Hour (maximum data loss window).
- **Recovery Time Objective (RTO):** < 5 Minutes (time required to complete restoration).
- **Zero Downtime Backup:** Backups run asynchronously using SQLite's online backup API without locking readers or writers.

---

## 2. Backup Architecture

The backup script `scripts/backup_db.py` creates self-verifying, timestamped snapshots:

1. Connects to `dukaandost.db` and `checkpoints.db`.
2. Invokes SQLite's C-level `source_conn.backup(dest_conn)`.
3. Executes `PRAGMA integrity_check;` on the backup file. If corrupted, it is automatically discarded.
4. Computes SHA-256 checksums of the backed-up files.
5. Calculates row counts across all relational tables (`users`, `stores`, `products`, `customers`, `transactions`, etc.).
6. Generates `backups/backup_manifest.json` recording backup metadata.

---

## 3. How to Execute Backups

### 3.1 Manual Backup
```bash
python scripts/backup_db.py
```
Output:
```
============================================================
DUKAANDOST AI - BACKUP SYSTEM
Timestamp: 2026-11-24T22:28:35.828078
============================================================
[*] Initiating atomic online backup: dukaandost.db -> dukaandost_backup_20261124_222835.db...
[+] Verified backup created successfully: dukaandost_backup_20261124_222835.db (405504 bytes)
[*] Initiating atomic online backup: checkpoints.db -> checkpoints_backup_20261124_222835.db...
[+] Verified backup created successfully: checkpoints_backup_20261124_222835.db (9543680 bytes)
[+] Manifest updated: backups/backup_manifest.json
[SUCCESS] Backup process completed with 100% integrity verification.
```

### 3.2 Automated Scheduled Cron (Linux / macOS)
Add to crontab (`crontab -e`) to backup hourly:
```cron
0 * * * * cd /opt/dukaandostai && /opt/dukaandostai/venv/bin/python scripts/backup_db.py >> /var/log/dukaandost_backup.log 2>&1
```

### 3.3 Windows Task Scheduler
Create a scheduled task running `python scripts\backup_db.py` every 4 hours.

---

## 4. How to Restore from Backup

The restore script `scripts/restore_db.py` guarantees safe restoration:

### 4.1 Restoring Latest Backup Automatically
```bash
python scripts/restore_db.py
```

### 4.2 Restoring from a Specific Backup File
```bash
python scripts/restore_db.py --file backups/dukaandost_backup_20261124_222835.db
```

### 4.3 Safety Guarantees During Restore
1. Pre-validates the target backup with `PRAGMA integrity_check;` and `PRAGMA foreign_key_check;`.
2. Creates an automatic safety snapshot (`backups/pre_restore_safety_YYYYMMDD_HHMMSS.db`) before modifying live data.
3. Performs atomic restoration.
4. Performs a post-restore integrity check on the live database.
