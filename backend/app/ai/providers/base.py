from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseAIProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the unique identifier of the provider (e.g. 'openai', 'gemini')."""
        pass

    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Returns list of supported model identifiers."""
        pass

    @abstractmethod
    async def test_connection(self, api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Tests API connectivity. Returns dict with:
        {"success": bool, "message": str, "latency_ms": float, "status": "CONNECTED AND VERIFIED" | "CONNECTION FAILED"}
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generates text completion. Returns dict with:
        {"text": str, "prompt_tokens": int, "completion_tokens": int, "latency_ms": float}
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates structured JSON output adhering to schema.
        """
        pass
