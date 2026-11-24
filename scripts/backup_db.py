#!/usr/bin/env python3
"""
DukaanDost AI - Automated Zero-Downtime Database Backup Utility
Uses SQLite's online backup API to take atomic, consistent snapshots
without locking the live application database.
"""

import os
import sys
import time
import shutil
import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"
DB_PATH = BASE_DIR / "dukaandost.db"
CHECKPOINTS_DB_PATH = BASE_DIR / "checkpoints.db"


def calculate_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def verify_sqlite_integrity(db_path: Path) -> bool:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        conn.close()
        return result is not None and result[0] == "ok"
    except Exception as e:
        print(f"[ERROR] Integrity check failed for {db_path}: {e}")
        return False


def get_table_counts(db_path: Path) -> dict:
    counts = {}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
            counts[tbl] = cursor.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"[WARN] Failed to fetch table counts: {e}")
    return counts


def backup_database(source_path: Path, dest_dir: Path, tag: str = "app") -> Path:
    if not source_path.exists():
        print(f"[SKIP] Source database {source_path} does not exist.")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_path = dest_dir / f"{tag}_backup_{timestamp}.db"

    print(f"[*] Initiating atomic online backup: {source_path.name} -> {dest_path.name}...")
    source_conn = sqlite3.connect(source_path)
    dest_conn = sqlite3.connect(dest_path)

    # SQLite online backup API
    source_conn.backup(dest_conn, pages=100, sleep=0.01)

    dest_conn.close()
    source_conn.close()

    if not verify_sqlite_integrity(dest_path):
        dest_path.unlink(missing_ok=True)
        raise RuntimeError(f"Corrupted backup created at {dest_path}!")

    print(f"[+] Verified backup created successfully: {dest_path.name} ({os.path.getsize(dest_path)} bytes)")
    return dest_path


def main():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 60)
    print("DUKAANDOST AI - BACKUP SYSTEM")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    backed_up_files = {}

    # 1. Primary app database
    if DB_PATH.exists():
        app_backup = backup_database(DB_PATH, BACKUP_DIR, tag="dukaandost")
        if app_backup:
            backed_up_files["app_db"] = {
                "file": app_backup.name,
                "size_bytes": os.path.getsize(app_backup),
                "sha256": calculate_sha256(app_backup),
                "table_counts": get_table_counts(app_backup)
            }

    # 2. Checkpoints database
    if CHECKPOINTS_DB_PATH.exists():
        chk_backup = backup_database(CHECKPOINTS_DB_PATH, BACKUP_DIR, tag="checkpoints")
        if chk_backup:
            backed_up_files["checkpoints_db"] = {
                "file": chk_backup.name,
                "size_bytes": os.path.getsize(chk_backup),
                "sha256": calculate_sha256(chk_backup),
                "table_counts": get_table_counts(chk_backup)
            }

    # 3. Write manifest
    manifest_path = BACKUP_DIR / "backup_manifest.json"
    manifest_data = {
        "latest_backup_timestamp": datetime.now().isoformat(),
        "backups": backed_up_files
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[+] Manifest updated: {manifest_path}")
    print("[SUCCESS] Backup process completed with 100% integrity verification.")


if __name__ == "__main__":
    main()
