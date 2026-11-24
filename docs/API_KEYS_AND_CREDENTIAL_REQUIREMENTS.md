# DukaanDost AI 2.0 - API Keys & Credential Requirements Registry

**Document Purpose:** Complete, authoritative inventory of all external services, credential requirements, official signup links, permissions, free alternatives, and live connection testing procedures.

---

## 1. Master Structured Integration Registry

| Service | Purpose | Required or Optional | Credential Type | Free Alternative | Current Status |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Groq Cloud API** | Fast LLM reasoning for conversational assistant and agents | **Recommended** | API Key (`gsk_...`) | Local Deterministic Engine | <span style="color:#16a34a; font-weight:700;">CONNECTED & VERIFIED</span> |
| **Google Gemini API** | Multimodal reasoning & secondary fallback AI provider | Optional | API Key (`AIza...`) | Groq API or Local Deterministic | <span style="color:#0284c7;">ADAPTER READY</span> |
| **OpenAI API** | High-precision commercial LLM reasoning (GPT-4o) | Optional | API Key (`sk-...`) | Groq API or Local Deterministic | <span style="color:#0284c7;">ADAPTER READY</span> |
| **Ollama Local Engine** | 100% private offline open-source LLM inference | Optional | Local Endpoint (`:11434`) | Built-in Deterministic Engine | <span style="color:#7e22ce;">WIRED (LOCAL)</span> |
| **SQLite (Default DB)** | Application data & LangGraph state persistence | **Mandatory** | File Path (`dukaandost.db`) | Included natively in Python | <span style="color:#16a34a; font-weight:700;">ACTIVE & VERIFIED</span> |
| **PostgreSQL (Prod DB)** | High-concurrency enterprise multi-tenant database | Optional | Database Connection URI | SQLite WAL Mode | <span style="color:#eab308;">DOCKER PROFILE READY</span> |
| **Twilio Messaging** | Outbound SMS and WhatsApp message transmission | Optional | Account SID & Auth Token | Local Sandboxed Preview | <span style="color:#0284c7;">DISPATCH CODE READY</span> |
| **Browser Speech API** | Voice recognition (speech-to-text) & read-aloud (TTS) | **Recommended** | Browser Native API | Free & Built into all browsers | <span style="color:#16a34a; font-weight:700;">INTEGRATED (₹0)</span> |
| **Open-Meteo Satellite** | Real-time live meteorological telemetry for Ranchi | **Recommended** | Open REST API (No Key) | None needed (Free public feed) | <span style="color:#16a34a; font-weight:700;">ACTIVE (15.9°C LIVE)</span> |
| **OpenWeatherMap** | Hyper-local commercial meteorological alerts | Optional | API Key (32-char hex) | Open-Meteo Satellite Feed | <span style="color:#0284c7;">ADAPTER WIRED</span> |
| **Google Sheets CSV** | Supplier catalog upload & margin reconciliation | **Recommended** | CSV File Upload | Built-in File Reader | <span style="color:#16a34a; font-weight:700;">ACTIVE & VERIFIED</span> |
| **Google OAuth 2.0** | Direct Google Drive / Google Sheets live sync | Optional | OAuth Client ID & Secret | Google Sheets CSV Export | <span style="color:#64748b;">OPTIONAL</span> |

---

## 2. Exhaustive 10-Point Integration Evaluation

---

### A. Groq Cloud API
1. **Why it is required:** Powers ultra-fast (sub-second) reasoning for the conversational AI assistant, strategy planner, and localized marketing copywriter.
2. **What functionality it enables:** Generates live answers in conversational Hindi, English, and Hinglish; formulates dynamic Kirana growth initiatives; writes customized promotional messages for Sharma Ji.
3. **Mandatory or Optional:** **Recommended** (already provided and verified active).
4. **Free alternative:** Built-in Deterministic Python Engine (operates 100% offline at ₹0 cost).
5. **Usage limits:** Groq Free Tier permits up to 30 requests per minute and 14,400 requests per day on open-weight models.
6. **Can it generate charges:** No charges under Groq Free Tier; billing requires explicit credit card attachment.
7. **Permissions required:** Standard developer inference API access.
8. **Where to create account:** Official Groq Console: [https://console.groq.com/](https://console.groq.com/)
9. **How to generate credential:** Log in to Groq Console -> Navigate to **API Keys** -> Click **"Create API Key"** -> Copy the `gsk_...` key.
10. **How to test connection:**
   ```bash
   python -c "import httpx; r = httpx.post('http://127.0.0.1:8000/api/ai/test-connection', json={'provider_name': 'groq', 'model': 'qwen/qwen3.8-27b'}); print(r.json())"
   ```

---

### B. Google Gemini API
1. **Why it is required:** Provides high-quality multimodal reasoning and serves as an automated fallback if Groq encounters rate limits.
2. **What functionality it enables:** Strategic retail analysis, Hindi/Hinglish copy generation, and potential receipt image inspection.
3. **Mandatory or Optional:** **Optional** (system works fully with Groq or Deterministic mode).
4. **Free alternative:** Groq Cloud API or Deterministic Engine.
5. **Usage limits:** Google AI Studio free tier provides up to 15 requests per minute (RPM) and 1 million tokens per minute on `gemini-2.0-flash`.
6. **Can it generate charges:** Free tier does not incur charges. Paid tier requires linking a Google Cloud billing account.
7. **Permissions required:** Generative Language API access.
8. **Where to create account:** Official Google AI Studio: [https://aistudio.google.com/](https://aistudio.google.com/)
9. **How to generate credential:** Sign in with Google Account -> Click **"Get API key"** -> Select or create a project -> Copy the `AIza...` key.
10. **How to test connection:**
   ```bash
   python -c "import httpx; r = httpx.post('http://127.0.0.1:8000/api/ai/test-connection', json={'provider_name': 'gemini'}); print(r.json())"
   ```

---

### C. OpenAI API
1. **Why it is required:** Industry-benchmark commercial LLM for high-precision business reasoning and structured JSON output.
2. **What functionality it enables:** Powers GPT-4o-mini / GPT-4o for complex Kirana supply chain diagnostics and marketing copy.
3. **Mandatory or Optional:** **Optional**.
4. **Free alternative:** Groq Cloud (`qwen/qwen3.8-27b`) or Deterministic Engine.
5. **Usage limits:** Governed by OpenAI API credit balance (Usage Tier 1: 500 RPM).
6. **Can it generate charges:** Yes, pay-per-token usage requires purchased credits.
7. **Permissions required:** Model inference access (`chat.completions`).
8. **Where to create account:** Official OpenAI Platform: [https://platform.openai.com/](https://platform.openai.com/)
9. **How to generate credential:** Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) -> Click **"Create new secret key"** -> Copy the `sk-...` key.
10. **How to test connection:** Tested via `POST /api/ai/test-connection` with `provider_name: "openai"`.

---

### D. Browser-Native Speech API (Voice & Audio)
1. **Why it is required:** Enables voice input and voice playback for the AI Business Assistant and Daily Business Briefing.
2. **What functionality it enables:**
   - Speech-to-Text: Speak questions in Hindi or English using the microphone.
   - Text-to-Speech: Read aloud the daily briefing and assistant responses with Play, Pause, Resume, and Stop controls.
3. **Mandatory or Optional:** **Included natively** (works in Chrome, Edge, Safari, Firefox).
4. **Free alternative:** Fully free, zero API key required, zero latency overhead.
5. **Usage limits:** Unlimited (runs locally in the user's web browser).
6. **Can it generate charges:** **₹0 (Zero cost guaranteed).**
7. **Permissions required:** Browser microphone permission prompt.
8. **Where to create account:** No account required.
9. **How to generate credential:** No credential needed; utilizes W3C Web Speech API standard (`window.speechSynthesis` and `webkitSpeechRecognition`).
10. **How to test connection:** Click the microphone or speaker button in the DukaanDost AI dashboard.

---

### E. Twilio Messaging (WhatsApp & SMS)
1. **Why it is required:** Transmits approved customer promotional campaigns and vouchers from the sandbox directly to real customer mobile phones.
2. **What functionality it enables:** Sends real WhatsApp messages via Twilio WhatsApp Sandbox and SMS messages to Indian mobile numbers (+91).
3. **Mandatory or Optional:** **Optional** (promotions run safely in sandbox mode without Twilio).
4. **Free alternative:** Built-in Sandboxed Preview (generates full bilingual copy for Sharma Ji to inspect without sending network SMS).
5. **Usage limits:** Twilio Free Trial provides ~$15 initial credit for verified numbers.
6. **Can it generate charges:** Free trial credit absorbed first; paid telecommunications carrier fees apply once trial balance expires.
7. **Permissions required:** Outbound SMS / Programmable Messaging permission.
8. **Where to create account:** Official Twilio Console: [https://console.twilio.com/](https://console.twilio.com/)
9. **How to generate credential:**
   - Sign up at Twilio Console -> Retrieve **Account SID** and **Auth Token** from dashboard.
   - For WhatsApp: Activate **Twilio WhatsApp Sandbox** under Messaging -> Try WhatsApp.
   - Configure in `.env`: `TWILIO_ACCOUNT_SID=...`, `TWILIO_AUTH_TOKEN=...`, `TWILIO_PHONE_NUMBER=...`.
10. **How to test connection:**
   ```bash
   python -c "from app.integrations.messaging import MessagingIntegration; print(MessagingIntegration.send_live_message('+91XXXXXXXXXX', 'Test from Sharma Store'))"
   ```

---

### F. Open-Meteo Satellite Feeds & OpenWeatherMap
1. **Why it is required:** Provides live weather context for Ranchi, Jharkhand to adjust Kirana demand forecasts (e.g. cold wave driving tea sales, monsoon humidity threatening open flour bags).
2. **What functionality it enables:** Automatically updates the **Live Ranchi Weather** widget with real-time temperature, humidity, and condition.
3. **Mandatory or Optional:** **Active & Operational**.
4. **Free alternative:** Open-Meteo is completely free, open-access, and requires zero API keys.
5. **Usage limits:** Up to 10,000 requests per day (Open-Meteo).
6. **Can it generate charges:** ₹0 (Zero cost).
7. **Permissions required:** None.
8. **Where to create account:** Optional OpenWeatherMap at [https://openweathermap.org/api](https://openweathermap.org/api).
9. **How to generate credential:** Not needed for Open-Meteo; for OpenWeatherMap, sign up and copy default 32-character key.
10. **How to test connection:**
   ```bash
   python -c "from app.integrations.weather import WeatherIntegration; print(WeatherIntegration.get_weather_signals('Ranchi'))"
   ```

---

### G. Google Sheets & CSV Data Pipeline
1. **Why it is required:** Allows Kirana store owners to import supplier wholesale catalogs and reconcile inventory without manual typing.
2. **What functionality it enables:** Upload CSV, schema verification, negative margin detection, preview with profit calculations, and atomic database import.
3. **Mandatory or Optional:** **Active & Operational**.
4. **Free alternative:** Fully local file parser built into Python (`csv` / `io` modules).
5. **Usage limits:** Unlimited.
6. **Can it generate charges:** ₹0 (Zero cost).
7. **Permissions required:** None for CSV upload.
8. **Where to create account:** No account required.
9. **How to generate credential:** Optional Google Cloud OAuth Client ID if connecting directly via Google Drive API.
10. **How to test connection:** Navigate to `/integrations` in dashboard, paste CSV template, click "Preview CSV Import".
