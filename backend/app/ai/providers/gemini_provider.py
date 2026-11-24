import time
import json
import httpx
from typing import Dict, Any, Optional, List
from app.ai.providers.base import BaseAIProvider
from app.config import settings

class GeminiProvider(BaseAIProvider):
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def get_provider_name(self) -> str:
        return "gemini"

    def get_supported_models(self) -> List[str]:
        return ["gemini-2.0-flash", "gemini-1.5-flash"]

    def _get_key(self, api_key: Optional[str] = None) -> Optional[str]:
        return api_key or getattr(settings, "GEMINI_API_KEY", None)

    async def test_connection(self, api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        key = self._get_key(api_key)
        if not key or key.strip() == "":
            return {
                "success": False,
                "status": "NOT CONFIGURED",
                "message": "Google Gemini API key is not configured.",
                "latency_ms": 0.0
            }

        start = time.time()
        m = model or "gemini-2.0-flash"
        url = f"{self.BASE_URL}/{m}:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": "ping"}]}],
            "generationConfig": {"maxOutputTokens": 5}
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                latency = round((time.time() - start) * 1000, 2)
                if res.status_code == 200:
                    return {
                        "success": True,
                        "status": "CONNECTED AND VERIFIED",
                        "message": f"Successfully connected to Google Gemini ({m}).",
                        "latency_ms": latency
                    }
                else:
                    err_msg = res.json().get("error", {}).get("message", res.text)
                    return {
                        "success": False,
                        "status": "CONNECTION FAILED",
                        "message": f"Gemini error ({res.status_code}): {err_msg}",
                        "latency_ms": latency
                    }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "success": False,
                "status": "CONNECTION FAILED",
                "message": f"Network error connecting to Gemini: {str(e)}",
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
            raise ValueError("Google Gemini API key is missing.")

        start = time.time()
        m = model or "gemini-2.0-flash"
        url = f"{self.BASE_URL}/{m}:generateContent?key={key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, json=payload)
            latency = round((time.time() - start) * 1000, 2)
            if res.status_code != 200:
                raise RuntimeError(f"Gemini API failed ({res.status_code}): {res.text}")

            data = res.json()
            candidates = data.get("candidates", [])
            text = candidates[0]["content"]["parts"][0]["text"] if candidates else ""
            meta = data.get("usageMetadata", {})
            return {
                "text": text,
                "prompt_tokens": meta.get("promptTokenCount", len(prompt.split())),
                "completion_tokens": meta.get("candidatesTokenCount", len(text.split())),
                "total_tokens": meta.get("totalTokenCount", len(prompt.split()) + len(text.split())),
                "latency_ms": latency,
                "provider": "gemini",
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
        key = self._get_key(api_key)
        if not key:
            raise ValueError("Google Gemini API key is missing.")

        start = time.time()
        m = model or "gemini-2.0-flash"
        url = f"{self.BASE_URL}/{m}:generateContent?key={key}"

        sys_text = (system_instruction or "") + "\nYou must output strictly valid JSON conforming to the requested response schema."
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": sys_text}]},
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, json=payload)
            latency = round((time.time() - start) * 1000, 2)
            if res.status_code != 200:
                raise RuntimeError(f"Gemini API failed ({res.status_code}): {res.text}")

            data = res.json()
            candidates = data.get("candidates", [])
            raw_text = candidates[0]["content"]["parts"][0]["text"] if candidates else "{}"
            meta = data.get("usageMetadata", {})
            return {
                "data": json.loads(raw_text),
                "prompt_tokens": meta.get("promptTokenCount", len(prompt.split())),
                "completion_tokens": meta.get("candidatesTokenCount", len(raw_text.split())),
                "total_tokens": meta.get("totalTokenCount", len(prompt.split()) + len(raw_text.split())),
                "latency_ms": latency,
                "provider": "gemini",
                "model": m
            }
