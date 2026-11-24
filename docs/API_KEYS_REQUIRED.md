# DUKAANDOST AI 2.0 — API KEYS & CREDENTIAL REQUIREMENTS
## Zero-Cost-First Integration Registry and Setup Guide

---

### Integration Registry

| Service | Purpose | Required / Optional | Credential Type | Environment Variable | Free Tier Available? | Potential Charges | Status |
|---|---|---|---|---|---|---|---|
| **Groq API** | Real-time fast LLM reasoning for Assistant & Briefing (`qwen-2.5-32b`, `llama-3.3-70b`) | Recommended | API Key | `GROQ_API_KEY` | Yes (Generous free tier with rpm limits) | None on free tier | **CONFIGURED & VERIFIED** |
| **Local Deterministic AI** | Offline fallback AI engine that runs completely locally | Mandatory Fallback | None (Local Python) | `USE_LOCAL_DETERMINISTIC_MODE=True` | Yes (100% free forever) | ₹0.00 | **CONNECTED & VERIFIED** |
| **Google Gemini API** | Secondary AI reasoning fallback (`gemini-2.0-flash`) | Optional | API Key | `GEMINI_API_KEY` | Yes (Free rate-limited tier) | Paid only if billing enabled | Optional / Not Configured |
| **OpenAI API** | Tertiary AI reasoning fallback (`gpt-4o-mini`) | Optional | API Key | `OPENAI_API_KEY` | No (Requires credit) | Usage-based | Optional / Not Configured |
| **Ollama Local** | Local open-weight models (`llama3.2`, `mistral`) | Optional | Local Host URL | `OLLAMA_BASE_URL` | Yes (Open source, runs on local machine) | ₹0.00 | Optional / Local |
| **Open-Meteo Weather** | Hyperlocal rainfall and temperature signals for Ranchi | Optional (Live) | None (Public API) | None required | Yes (100% free open API) | ₹0.00 | **LIVE & OPERATIONAL** |
| **Web Speech API** | Natural voice playback and microphone recognition | Mandatory Voice | Browser Native | Built-in | Yes (Standard browser feature) | ₹0.00 | **ENABLED & VERIFIED** |
| **WhatsApp Business** | Promotional customer campaigns | Optional | Meta Cloud API Token | `WHATSAPP_TOKEN` | Yes (1,000 free service conversations/month) | Meta rate card above limit | Sandbox / Draft Mode |

---

### Zero-Cost-First Principle
1. **Never require paid services:** If all external API keys are absent, DukaanDost AI operates deterministically without degradation of core business operations.
2. **Never commit secrets:** All credentials reside in the uncommitted `.env` file and are never sent to the browser or committed to GitHub.
3. **No surprise billing:** The system strictly rejects third-party services that require paid credit cards or paid subscription activation.
