# DukaanDost AI - Deployment & Operations Guide

## 1. System Requirements

- **Operating System:** Linux, macOS, or Windows 10/11
- **Python:** 3.11 or higher
- **Node.js:** 20.x or higher (with npm)
- **Docker:** Docker Engine 24+ and Docker Compose v2 (optional for containerized deployment)

---

## 2. Local Bare-Metal Development Setup

### 2.1 Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-org/dukaandostai.git
cd dukaandostai

# Set up Python virtual environment
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database schema
python -c "from app.database.connection import init_db; init_db()"

# Start FastAPI server on port 8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API documentation is now live at: `http://127.0.0.1:8000/docs`.

### 2.2 Frontend Setup
```bash
# In a separate terminal:
cd frontend

# Install npm packages
npm install

# Start Vite dev server on port 5173
npm run dev -- --host 127.0.0.1 --port 5173
```
The web dashboard is now accessible at: `http://127.0.0.1:5173`.

---

## 3. Containerized Deployment (Docker Compose)

### 3.1 Standard Deployment (SQLite Persistence)
```bash
# Build and run backend and frontend containers
docker-compose up -d --build

# View container status and healthchecks
docker-compose ps

# View backend logs
docker-compose logs -f backend
```
- Frontend UI: `http://localhost:5173` (or `http://localhost:80`)
- Backend API: `http://localhost:8000`
- API Healthcheck: `http://localhost:8000/api/health/live`

### 3.2 Enterprise Production (PostgreSQL Scaling)
To start with a managed PostgreSQL 16 container:
```bash
docker-compose --profile postgres up -d --build
```

---

## 4. Environment Variables Reference

Create a `.env` file in the project root:

```ini
# Application Environment
APP_ENV=development                   # development | production | test
DEBUG=true

# AI Provider Configuration (Zero-Cost Default)
AI_MODE=deterministic                # deterministic | openai | gemini | groq | ollama
OPENAI_API_KEY=                      # Optional
GEMINI_API_KEY=                      # Optional
GROQ_API_KEY=                        # Optional
OLLAMA_BASE_URL=http://127.0.0.1:11434

# Security & JWT Tokens
JWT_SECRET_KEY=dukaandost_super_secret_signing_key_change_in_prod
ACCESS_TOKEN_EXPIRE_MINUTES=1440      # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration
DATABASE_URL=sqlite:///./dukaandost.db
CHECKPOINT_DB_PATH=./checkpoints.db

# Server Bindings
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

---

## 5. Verification & Health Monitoring

Run these curl commands to verify your deployment:

```bash
# Verify backend liveness
curl -i http://127.0.0.1:8000/api/health/live

# Verify database connection readiness
curl -i http://127.0.0.1:8000/api/health/ready

# Inspect memory, CPU, and zero-cost status
curl -i http://127.0.0.1:8000/api/health/system
```
