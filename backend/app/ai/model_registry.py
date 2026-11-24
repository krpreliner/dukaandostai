from typing import Dict, Any, List

# Official verified pricing per 1M tokens (as of late 2024 / 2025)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # OpenAI
    "gpt-4o-mini": {"prompt_per_1m": 0.15, "completion_per_1m": 0.60},
    "gpt-4o": {"prompt_per_1m": 2.50, "completion_per_1m": 10.00},
    # Google Gemini
    "gemini-2.0-flash": {"prompt_per_1m": 0.10, "completion_per_1m": 0.40},
    "gemini-1.5-flash": {"prompt_per_1m": 0.075, "completion_per_1m": 0.30},
    # Groq Models
    "qwen/qwen3.8-27b": {"prompt_per_1m": 0.20, "completion_per_1m": 0.20},
    "openai/gpt-oss-120b": {"prompt_per_1m": 0.60, "completion_per_1m": 0.80},
    "openai/gpt-oss-20b": {"prompt_per_1m": 0.10, "completion_per_1m": 0.15},
    "llama-3.3-70b-versatile": {"prompt_per_1m": 0.59, "completion_per_1m": 0.79},
    "llama-3.1-8b-instant": {"prompt_per_1m": 0.05, "completion_per_1m": 0.08},
    # Ollama / Local
    "llama3": {"prompt_per_1m": 0.0, "completion_per_1m": 0.0},
    "mistral": {"prompt_per_1m": 0.0, "completion_per_1m": 0.0},
    "qwen2.5": {"prompt_per_1m": 0.0, "completion_per_1m": 0.0},
    # Deterministic Engine
    "local-deterministic-v1": {"prompt_per_1m": 0.0, "completion_per_1m": 0.0}
}

def calculate_cost_usd(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculates estimated cost in USD based on transparent published pricing."""
    pricing = MODEL_PRICING.get(model_name)
    if not pricing:
        return 0.0
    cost = (prompt_tokens * pricing["prompt_per_1m"] / 1_000_000.0) + \
           (completion_tokens * pricing["completion_per_1m"] / 1_000_000.0)
    return round(cost, 6)
