# DukaanDost AI - AI Provider & Multi-Model Setup Guide

## 1. Zero-Cost-First Philosophy

DukaanDost AI adheres to a strict **Zero-Cost-First Policy**:
- The platform functions **100% offline out-of-the-box** using an integrated deterministic intelligence engine.
- No paid API keys, paid subscriptions, or credit cards are ever required.
- All core agent decisions, financial margin checks, inventory calculations, and Hindi/English draft generation execute locally in **under 2 milliseconds** at **₹0 cost**.

Optional cloud LLM providers (OpenAI, Google Gemini, Groq) and local open-source LLMs (Ollama) can be attached at runtime for enhanced natural language reasoning.

---

## 2. Supported AI Providers & Models

| Provider | Supported Models | Cost per 1M Tokens (Input / Output) | Requires API Key? | Ideal Use Case |
| :--- | :--- | :--- | :---: | :--- |
| **Deterministic (Built-in)** | `local-deterministic-v1` | **$0.00 / $0.00 (₹0)** | **No** | Default offline production, zero risk, 100% reproducible |
| **Google Gemini** | `gemini-2.0-flash`, `gemini-1.5-flash` | $0.10 / $0.40 | Yes | Fast multimodal reasoning, free-tier available |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o` | $0.15 / $0.60 | Yes | High-precision commercial Kirana copy |
| **Groq** | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant` | $0.05 / $0.08 | Yes | Ultra-low latency open-weight inference |
| **Ollama (Local)** | `llama3`, `mistral`, `qwen2.5` | **$0.00 / $0.00 (₹0)** | **No** | 100% private local LLM inference on localhost:11434 |

---

## 3. Intelligent Fallback Architecture (`AIRouter`)

The `AIRouter` guarantees uninterrupted system execution through an automated three-tiered failover pipeline:

```
[Agent Request]
       |
       v
+---------------------------------------+
|  Tier 1: Configured Primary Provider   |  (e.g., Groq / Gemini)
+---------------------------------------+
       |
       +---> Succeeded: Log usage & return response
       |
       +---> Failed (Timeout / Invalid Key / Rate Limit)
       v
+---------------------------------------+
|  Tier 2: Configured Fallback Provider  |  (e.g., Ollama / OpenAI)
+---------------------------------------+
       |
       +---> Succeeded: Log fallback event & return response
       |
       +---> Failed (Network unreachable)
       v
+---------------------------------------+
|  Tier 3: Local Deterministic Engine   |  (Guaranteed 100% Uptime, ₹0 Cost)
+---------------------------------------+
       |
       +---> Always succeeds: Log degraded mode event & return response
```

Every AI call logs its provider, model, token usage, calculated cost in USD/INR, latency, and status in the `ai_usage_logs` database table.

---

## 4. Prompt Injection Defense & Sanitization

To protect LLM system prompts against injection attacks from customer inputs or external CSV catalog descriptions, all incoming untrusted strings are processed through `PromptManager.sanitize_untrusted_input()`:

- Scans for injection vectors: `ignore previous instructions`, `system prompt`, `developer mode`, `bypass safety`.
- Replaces matches with `[FILTERED_INSTRUCTION]`.
- Strips executable HTML/script tags.
- Enforces a 2,000 character maximum safe context window.
- Injects standardized bilingual system instructions (Hindi & English Kirana domain rules) to maintain persona integrity.

---

## 5. How to Configure Providers via the Web Dashboard

1. Navigate to **AI Providers & Costs** (`/providers`) in the dashboard sidebar.
2. Under **Provider Settings**:
   - Choose your preferred **Primary Provider** and **Fallback Provider**.
   - Select the target model from the dropdown.
   - Enter your provider API Key (stored encrypted in the database per store workspace).
3. Click **"Test Connection"** to verify latency and API key validity before saving.
4. Review cumulative token usage and cost metrics in the **Usage Analytics** table.
