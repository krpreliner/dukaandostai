# DukaanDost AI - Database Architecture & Migration Guide

## 1. Relational Schema Overview

DukaanDost AI maintains a clean, normalized relational schema designed for multi-tenant retail operations.

```
+----------------------------------------------------------------------------------------------------+
|                                      DATABASE SCHEMA OVERVIEW                                      |
+----------------------------------------------------------------------------------------------------+

  [stores] (store_id, name, location, owner_name)
     |
     +---< [store_members] >--- [users] (id, email, password_hash, full_name, is_active)
     |
     +---< [customers] (customer_id, store_id, name, phone, segment, visits, spent, status)
     |
     +---< [products] (product_id, store_id, name, category, cost, sell, stock, status)
     |
     +---< [transactions] (tx_id, store_id, customer_id, product_id, units, revenue, cost, profit)
     |
     +---< [expenses] (expense_id, store_id, category, amount, description, date)
     |
     +---< [execution_records] (execution_id, store_id, goal, net_income, status, started, completed)
     |
     +---< [task_records] (task_id, store_id, execution_id, agent_name, title, expected_impact, status)
     |
     +---< [approval_records] (approval_id, store_id, task_id, risk_level, status, decided_by)
     |
     +---< [failure_records] (failure_id, store_id, task_id, error_type, resolution_status)
     |
     +---< [audit_logs] (log_id, store_id, event_type, agent_name, details, timestamp)
     |
     +---< [ai_provider_settings] (setting_id, store_id, provider_name, is_primary, is_fallback)
     |
     +---< [ai_usage_logs] (log_id, store_id, provider, model, tokens, cost_usd, status)
     |
     +---< [integration_settings] (setting_id, store_id, integration_type, config_json)
```

---

## 2. Multi-Tenant Isolation Strategy

1. **Discriminator Column:** Every entity table includes a `store_id VARCHAR(50)` column indexed for rapid tenant-filtered queries.
2. **Query Scoping:** All repository queries (`BusinessRepository`) explicitly filter by `store_id`:
   ```python
   def get_products(self, store_id: str = "STORE_001"):
       return self.db.query(Product).filter(Product.store_id == store_id).all()
   ```
3. **Transport Security:** HTTP requests supply the tenant identifier via `X-Store-Id` header, validated against the calling user's authenticated `StoreMember` records. Cross-tenant access without membership produces `403 Forbidden`.

---

## 3. SQLite vs. PostgreSQL Deployment

The system is database-agnostic using SQLAlchemy ORM:

### 3.1 Local Development / Single Node (Default)
```ini
DATABASE_URL=sqlite:///./dukaandost.db
CHECKPOINT_DB_PATH=./checkpoints.db
```
- Fully self-contained, zero external daemons, works immediately offline.
- Concurrent read support via SQLite WAL mode (`PRAGMA journal_mode=WAL;`).

### 3.2 Production Cloud / Multi-Node
```ini
DATABASE_URL=postgresql+psycopg2://dukaandost_user:password@postgres:5432/dukaandost
CHECKPOINT_DB_PATH=postgresql+psycopg2://dukaandost_user:password@postgres:5432/dukaandost_checkpoints
```
- High concurrency, connection pooling (SQLAlchemy `QueuePool`), native row-level locking.

---

## 4. Alembic Versioned Migrations

Alembic tracks schema revisions deterministically in the `alembic_version` table.

### 4.1 Running Migrations
To upgrade the schema to the latest version:
```bash
alembic upgrade head
```

### 4.2 Checking Migration Status
```bash
alembic current
```

### 4.3 Generating a New Migration
```bash
alembic revision --autogenerate -m "add_supplier_lead_time"
```

### 4.4 Non-Destructive Auto-Migration
In development, `backend/app/database/migrations.py` runs `run_schema_migrations()` on startup. It uses SQLite table inspection to safely execute `ALTER TABLE ... ADD COLUMN` without deleting existing customer or transaction records.

---

## 5. Automated Backup & Recovery

- **Atomic Online Backups:** `python scripts/backup_db.py`
  - Utilizes SQLite's C-level online backup API (`source.backup(dest)`).
  - Guarantees 0 lock contention during live application use.
  - Verifies database integrity (`PRAGMA integrity_check`) before writing manifest.
- **Verified Restores:** `python scripts/restore_db.py --file backups/<FILE>.db`
  - Creates a safety pre-restore snapshot of the active database before applying changes.
  - Verifies foreign key constraints (`PRAGMA foreign_key_check`) post-restore.
