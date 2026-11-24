import time
import json
import httpx
from typing import Dict, Any, Optional, List
from app.ai.providers.base import BaseAIProvider
from app.config import settings

class OpenAIProvider(BaseAIProvider):
    API_URL = "https://api.openai.com/v1/chat/completions"

    def get_provider_name(self) -> str:
        return "openai"

    def get_supported_models(self) -> List[str]:
        return ["gpt-4o-mini", "gpt-4o"]

    def _get_key(self, api_key: Optional[str] = None) -> Optional[str]:
        return api_key or getattr(settings, "OPENAI_API_KEY", None)

    async def test_connection(self, api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        key = self._get_key(api_key)
        if not key or key.strip() == "":
            return {
                "success": False,
                "status": "NOT CONFIGURED",
                "message": "OpenAI API key is not configured.",
                "latency_ms": 0.0
            }

        start = time.time()
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": model or "gpt-4o-mini",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.API_URL, headers=headers, json=payload)
                latency = round((time.time() - start) * 1000, 2)
                if res.status_code == 200:
                    return {
                        "success": True,
                        "status": "CONNECTED AND VERIFIED",
                        "message": f"Successfully connected to OpenAI ({model or 'gpt-4o-mini'}).",
                        "latency_ms": latency
                    }
                else:
                    err_msg = res.json().get("error", {}).get("message", res.text)
                    return {
                        "success": False,
                        "status": "CONNECTION FAILED",
                        "message": f"OpenAI error ({res.status_code}): {err_msg}",
                        "latency_ms": latency
                    }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "status": "CONNECTION FAILED",
                "message": f"Network error connecting to OpenAI: {str(e)}",
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
        key = self._get_key(api_key)
        if not key:
            raise ValueError("OpenAI API key is missing.")

        start = time.time()
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model or "gpt-4o-mini",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(self.API_URL, headers=headers, json=payload)
            latency = round((time.time() - start) * 1000, 2)
            if res.status_code != 200:
                raise RuntimeError(f"OpenAI API failed ({res.status_code}): {res.text}")

            data = res.json()
            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "text": choice,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "latency_ms": latency,
                "provider": "openai",
                "model": model or "gpt-4o-mini"
            }

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        key = self._get_key(api_key)
        if not key:
            raise ValueError("OpenAI API key is missing.")

        start = time.time()
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        system_msg = (system_instruction or "") + "\nRespond strictly in valid JSON matching the schema."
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": model or "gpt-4o-mini",
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(self.API_URL, headers=headers, json=payload)
            latency = round((time.time() - start) * 1000, 2)
            if res.status_code != 200:
                raise RuntimeError(f"OpenAI API failed ({res.status_code}): {res.text}")

            data = res.json()
            raw_text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "data": json.loads(raw_text),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "latency_ms": latency,
                "provider": "openai",
                "model": model or "gpt-4o-mini"
            }
