import time
import json
import httpx
from typing import Dict, Any, Optional, List
from app.ai.providers.base import BaseAIProvider
from app.config import settings

class OllamaProvider(BaseAIProvider):
    def get_provider_name(self) -> str:
        return "ollama"

    def get_supported_models(self) -> List[str]:
        return ["llama3", "mistral", "qwen2.5"]

    def _get_base_url(self) -> str:
        return getattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")

    async def test_connection(self, api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        base_url = self._get_base_url()
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{base_url}/api/tags")
                latency = round((time.time() - start) * 1000, 2)
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {
                        "success": True,
                        "status": "CONNECTED AND VERIFIED",
                        "message": f"Connected to local Ollama. Available models: {', '.join(models) if models else 'None'}",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "success": False,
                        "status": "CONNECTION FAILED",
                        "message": f"Ollama daemon returned status {res.status_code}",
                        "latency_ms": latency
                    }
        except Exception:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "status": "NOT CONFIGURED",
                "message": f"Local Ollama daemon not reachable at {base_url}. Start Ollama locally if needed.",
                "latency_ms": latency
            }

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        base_url = self._get_base_url()
        m = model or "llama3"
        start = time.time()
        payload = {
            "model": m,
            "prompt": prompt,
            "system": system_instruction or "",
            "stream": False,
            "options": {"temperature": temperature}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(f"{base_url}/api/generate", json=payload)
            latency = round((time.time() - start) * 1000, 2)
            if res.status_code != 200:
                raise RuntimeError(f"Ollama generation failed ({res.status_code}): {res.text}")

            data = res.json()
            resp_text = data.get("response", "")
            return {
                "text": resp_text,
                "prompt_tokens": data.get("prompt_eval_count", len(prompt.split())),
                "completion_tokens": data.get("eval_count", len(resp_text.split())),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                "latency_ms": latency,
                "provider": "ollama",
                "model": m
            }

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        base_url = self._get_base_url()
        m = model or "llama3"
        start = time.time()
        sys_msg = (system_instruction or "") + "\nRespond with strictly valid JSON only."
        payload = {
            "model": m,
            "prompt": prompt,
            "system": sys_msg,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.2}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(f"{base_url}/api/generate", json=payload)
            latency = round((time.time() - start) * 1000, 2)
            if res.status_code != 200:
                raise RuntimeError(f"Ollama structured generation failed ({res.status_code}): {res.text}")

            data = res.json()
            raw_text = data.get("response", "{}")
            return {
                "data": json.loads(raw_text),
                "prompt_tokens": data.get("prompt_eval_count", len(prompt.split())),
                "completion_tokens": data.get("eval_count", len(raw_text.split())),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                "latency_ms": latency,
                "provider": "ollama",
                "model": m
            }
