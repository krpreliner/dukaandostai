#!/usr/bin/env python3
"""
DukaanDost AI - Verified Database Restore Utility
Validates backup integrity, generates pre-restore snapshot of live database,
and performs atomic restoration.
"""

import os
import sys
import shutil
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
DB_PATH = BASE_DIR / "dukaandost.db"


def verify_sqlite_integrity(db_path: Path) -> bool:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        cursor.execute("PRAGMA foreign_key_check;")
        fk_errors = cursor.fetchall()
        conn.close()
        return result is not None and result[0] == "ok" and len(fk_errors) == 0
    except Exception as e:
        print(f"[ERROR] Integrity check failed: {e}")
        return False


def get_latest_backup(prefix: str = "dukaandost_backup_") -> Path:
    if not BACKUP_DIR.exists():
        return None
    backups = sorted(BACKUP_DIR.glob(f"{prefix}*.db"), key=os.path.getmtime, reverse=True)
    return backups[0] if backups else None


def restore_database(backup_path: Path, target_path: Path):
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found at {backup_path}")

    print(f"[*] Verifying integrity of backup file {backup_path.name}...")
    if not verify_sqlite_integrity(backup_path):
        raise RuntimeError("Target backup file failed SQLite integrity check! Aborting restore.")
    print("[+] Backup file integrity verified (PRAGMA integrity_check = OK, foreign_key_check = OK).")

    # Create safety pre-restore snapshot if live database exists
    if target_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_path = BACKUP_DIR / f"pre_restore_safety_{timestamp}.db"
        print(f"[*] Creating pre-restore safety copy: {safety_path.name}...")
        shutil.copy2(target_path, safety_path)
        print("[+] Safety copy saved.")

    print(f"[*] Restoring {backup_path.name} -> {target_path.name}...")
    # Atomic online copy
    src_conn = sqlite3.connect(backup_path)
    dest_conn = sqlite3.connect(target_path)
    src_conn.backup(dest_conn)
    dest_conn.close()
    src_conn.close()

    print("[*] Performing post-restore integrity check on live database...")
    if not verify_sqlite_integrity(target_path):
        raise RuntimeError("Post-restore verification failed! Check database.")

    print(f"[SUCCESS] Database successfully restored from {backup_path.name}.")


def main():
    parser = argparse.ArgumentParser(description="DukaanDost AI Database Restore Utility")
    parser.add_argument("--file", type=str, help="Specific backup file path to restore", default=None)
    args = parser.parse_args()

    if args.file:
        backup_file = Path(args.file)
    else:
        backup_file = get_latest_backup()
        if not backup_file:
            print("[ERROR] No backups found in backups/ directory.")
            sys.exit(1)

    print("=" * 60)
    print("DUKAANDOST AI - RESTORE SYSTEM")
    print(f"Selected Backup: {backup_file.name}")
    print(f"Target Database: {DB_PATH.name}")
    print("=" * 60)

    restore_database(backup_file, DB_PATH)


if __name__ == "__main__":
    main()
