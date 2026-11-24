import os
import sqlite3
from typing import Optional
from langgraph.checkpoint.sqlite import SqliteSaver
from app.config import settings

_db_conn: Optional[sqlite3.Connection] = None
_checkpointer: Optional[SqliteSaver] = None

def get_checkpointer() -> SqliteSaver:
    global _db_conn, _checkpointer
    if _checkpointer is None or _db_conn is None:
        db_path = settings.CHECKPOINT_DB_PATH
        # Ensure directory exists if needed
        dirname = os.path.dirname(db_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
            
        _db_conn = sqlite3.connect(db_path, check_same_thread=False)
        _checkpointer = SqliteSaver(_db_conn)
        _checkpointer.setup()
    return _checkpointer

def close_checkpointer():
    global _db_conn, _checkpointer
    if _db_conn:
        try:
            _db_conn.close()
        except Exception:
            pass
        _db_conn = None
        _checkpointer = None
