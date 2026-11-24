import sqlite3
import logging
from sqlalchemy import inspect, text
from app.database.connection import engine, init_db

logger = logging.getLogger(__name__)

def run_schema_migrations():
    """
    Applies additive migrations safely to ensure all tables have required multi-tenant
    and audit columns without dropping or modifying existing data records.
    """
    init_db()  # Creates any brand new tables (e.g. users, stores, store_members, ai_provider_settings, etc.)

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Tables that require store_id
    tenant_tables = [
        "customers", "products", "transactions", "expenses",
        "execution_records", "task_records", "approval_records",
        "audit_logs", "failure_records"
    ]

    with engine.connect() as conn:
        for table in tenant_tables:
            if table in existing_tables:
                columns = [col["name"] for col in inspector.get_columns(table)]
                if "store_id" not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN store_id VARCHAR(50) DEFAULT 'STORE_001'"))
                        conn.commit()
                        logger.info(f"Added 'store_id' column to table '{table}'")
                    except Exception as e:
                        logger.warning(f"Could not add store_id to {table}: {e}")

        # Ensure ai_provider_settings has api_key
        if "ai_provider_settings" in existing_tables:
            cols = [col["name"] for col in inspector.get_columns("ai_provider_settings")]
            if "api_key" not in cols:
                try:
                    conn.execute(text("ALTER TABLE ai_provider_settings ADD COLUMN api_key TEXT"))
                    conn.commit()
                    logger.info("Added 'api_key' column to ai_provider_settings")
                except Exception as e:
                    logger.warning(f"Could not add api_key to ai_provider_settings: {e}")

if __name__ == "__main__":
    run_schema_migrations()
    print("Schema migration completed successfully.")
