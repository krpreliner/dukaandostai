# DukaanDost AI - Troubleshooting & Diagnostic Guide

## 1. Quick Diagnostic Commands

Before troubleshooting individual components, run the integrated health probes:

```bash
# Check Backend Health and Process Metrics
curl -s http://127.0.0.1:8000/api/health/system | jq .

# Verify Active Database Integrity
python -c "import sqlite3; conn = sqlite3.connect('dukaandost.db'); print(conn.execute('PRAGMA integrity_check;').fetchone()[0])"

# Run Full Test Suite
pytest backend/tests/ -v
```

---

## 2. Common Scenarios & Resolutions

### 2.1 Port Already in Use (Port 8000 or 5173)
- **Symptom:** `OSError: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): address already in use`
- **Cause:** A previous instance of Uvicorn or Vite is still running in the background.
- **Resolution (Windows PowerShell):**
  ```powershell
  # Find PID listening on port 8000
  Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess -Unique
  # Terminate process
  Stop-Process -Id <PID> -Force
  ```
- **Resolution (Linux / macOS):**
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```

---

### 2.2 Database Locked (`sqlite3.OperationalError: database is locked`)
- **Symptom:** Requests hang or return `500 Internal Server Error` with `database is locked`.
- **Cause:** Multiple concurrent transactions attempting write operations while WAL mode is disabled.
- **Resolution:**
  Enable Write-Ahead Logging (WAL) mode:
  ```bash
  python -c "import sqlite3; conn = sqlite3.connect('dukaandost.db'); conn.execute('PRAGMA journal_mode=WAL;'); conn.close(); print('WAL mode enabled.')"
  ```
  Ensure database connection pool uses appropriate `timeout=30.0` in `backend/app/database/connection.py`.

---

### 2.3 Authentication Errors (401 Unauthorized / 403 Forbidden)
- **Symptom:** Dashboard shows `Access denied: User is not a member of store 'STORE_001'`.
- **Cause:** Either the JWT access token has expired (default lifetime is 24 hours), or the selected store workspace in the UI does not match the user's authorized memberships.
- **Resolution:**
  1. Click **Logout** in the top navigation header and log in again using the seeded demo credentials (`owner@sharmastore.com` / `SharmaStore2026!`).
  2. Check the active store selector dropdown in the top bar to verify you are on `Sharma General Store (STORE_001)`.
  3. Inspect `/api/auth/me` response via browser DevTools Network tab.

---

### 2.4 External AI Provider Fails or Rate Limits
- **Symptom:** AI Provider status turns red or requests show `RateLimitError`.
- **Cause:** Cloud provider (OpenAI, Gemini, Groq) quota exceeded or invalid API key.
- **Built-in Resilience:** The platform **automatically degrades gracefully** to the local deterministic engine. Workflow runs will continue without interruption.
- **Resolution:**
  1. Visit `/providers` in the dashboard.
  2. Click **"Test Connection"** next to the provider to view exact latency and upstream error messages.
  3. Switch primary provider to **Deterministic Mode** or update the API key.

---

### 2.5 Google Sheets CSV Import Errors
- **Symptom:** CSV import preview displays `Missing required columns`.
- **Cause:** The CSV header does not match the required schema.
- **Resolution:**
  Ensure the first line of your CSV contains:
  ```csv
  product_id,product_name,category,cost_price,selling_price,current_stock,supplier_name
  ```
  Ensure `selling_price` is strictly greater than or equal to `cost_price` to prevent negative margin imports.
