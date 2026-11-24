from typing import Dict, Any, Optional, List
from app.ai.providers.base import BaseAIProvider
from app.ai.providers.deterministic_provider import DeterministicProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.providers.ollama_provider import OllamaProvider

class ProviderManager:
    _instance = None

    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {
            "deterministic": DeterministicProvider(),
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "groq": GroqProvider(),
            "ollama": OllamaProvider()
        }

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ProviderManager()
        return cls._instance

    def get_provider(self, name: str) -> BaseAIProvider:
        return self.providers.get(name.lower(), self.providers["deterministic"])

    def list_providers(self) -> List[str]:
        return list(self.providers.keys())

    async def test_all_providers(self) -> Dict[str, Any]:
        results = {}
        for name, provider in self.providers.items():
            results[name] = await provider.test_connection()
        return results
