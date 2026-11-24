# DUKAANDOST AI 2.0 — ENVIRONMENT & CONFIGURATION GUIDE
## Configuration Parameters, Secrets Handling & Deployment Settings

---

### 1. Overview
DukaanDost AI adheres to twelve-factor app principles. All configuration values are loaded from environment variables or a local `.env` file via `app.config.settings` (Pydantic `BaseSettings`).

> [!CAUTION]
> Never commit `.env` or real API keys to version control. The repository `.gitignore` strictly ignores `.env`, `.env.local`, and all `*.db` files.

---

### 2. Environment Variables Specification

| Variable Name | Required? | Default Value | Purpose & Description |
|---|---|---|---|
| `APP_NAME` | No | `DukaanDost AI` | Name of the application displayed across UI headers and logs. |
| `APP_ENV` | No | `development` | Deployment environment (`development`, `staging`, `production`). |
| `DATABASE_URL` | No | `sqlite:///./dukaandost.db` | Primary database connection string (SQLite for local dev, PostgreSQL for production). |
| `CHECKPOINT_DB_PATH` | No | `checkpoints.db` | File path for SQLite-backed LangGraph execution state checkpoints. |
| `AI_MODE` | No | `groq` | Default AI execution mode: `groq`, `deterministic`, `openai`, `gemini`, or `ollama`. |
| `USE_LOCAL_DETERMINISTIC_MODE` | No | `False` | Forces 100% offline deterministic rule engine if set to `True` (zero cloud dependencies). |
| `GROQ_API_KEY` | Recommended | *(none)* | Groq Cloud API key for ultra-fast conversational reasoning (`qwen-2.5-32b`, `llama-3.3-70b`). |
| `GEMINI_API_KEY` | Optional | *(none)* | Google Gemini API key for fallback reasoning (`gemini-2.0-flash`). |
| `OPENAI_API_KEY` | Optional | *(none)* | OpenAI API key for fallback reasoning (`gpt-4o-mini`). |
| `OLLAMA_BASE_URL` | Optional | `http://localhost:11434` | Base URL for local self-hosted Ollama model server. |
| `JWT_SECRET_KEY` | Mandatory | *(auto-generated)* | 256-bit cryptographically secure key for signing HS256 JWT auth tokens. |
| `JWT_ALGORITHM` | No | `HS256` | Cryptographic algorithm for JWT tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Lifespan of access tokens before requiring refresh. |
| `MAX_PROMOTIONAL_DISCOUNT_PCT`| No | `15.0` | Mandatory financial guardrail: absolute ceiling on promotional markdown percentage. |
| `MIN_GROSS_MARGIN_PCT` | No | `5.0` | Mandatory financial guardrail: minimum acceptable gross profit margin threshold. |
| `CORS_ORIGINS` | No | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed frontend origins for CORS security. |

---

### 3. Setup Instructions

#### Step 1: Clone Repository
```bash
git clone https://github.com/krpreliner/dukaandostai.git
cd dukaandostai
```

#### Step 2: Create `.env` from Example
```bash
cp .env.example .env
```
Edit `.env` and configure your `GROQ_API_KEY` (or leave blank to operate in local deterministic mode).

#### Step 3: Run Backend
```bash
# Python 3.11+
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r backend/requirements.txt
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Step 4: Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:5173/](http://localhost:5173/)** in your web browser.
