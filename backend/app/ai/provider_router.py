import logging
import asyncio
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.ai.provider_manager import ProviderManager
from app.ai.prompt_manager import PromptManager
from app.ai.model_registry import calculate_cost_usd
from app.database.repository import BusinessRepository
from app.config import settings

logger = logging.getLogger(__name__)

class AIRouter:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.manager = ProviderManager.get_instance()

    async def route_text_generation(
        self,
        prompt: str,
        agent_name: str = "General",
        store_id: str = "STORE_001",
        execution_id: Optional[str] = None,
        max_tokens: int = 800
    ) -> Dict[str, Any]:
        """
        Executes text generation with intelligent fallback:
        Primary Provider -> Fallback Provider -> Deterministic Local Mode.
        """
        sanitized_prompt = PromptManager.sanitize_untrusted_input(prompt)
        sys_inst = PromptManager.get_system_instruction(agent_name)

        # Check DB settings if available
        primary_name = "deterministic"
        fallback_name = None
        provider_keys = {}
        provider_models = {}

        if self.db:
            repo = BusinessRepository(self.db)
            db_settings = repo.get_ai_provider_settings(store_id=store_id)
            for s in db_settings:
                if s.api_key:
                    provider_keys[s.provider_name] = s.api_key
                if s.model_name:
                    provider_models[s.provider_name] = s.model_name
                if s.is_primary and s.is_enabled:
                    primary_name = s.provider_name
                elif s.is_fallback and s.is_enabled:
                    fallback_name = s.provider_name

        # If settings env override or keys exist in env
        ai_mode = getattr(settings, "AI_MODE", "deterministic").lower()
        if ai_mode != "deterministic":
            primary_name = ai_mode
        elif getattr(settings, "GEMINI_API_KEY", None):
            primary_name = "gemini"
        elif getattr(settings, "OPENAI_API_KEY", None):
            primary_name = "openai"
        elif getattr(settings, "GROQ_API_KEY", None):
            primary_name = "groq"

        # Attempt sequence
        candidates = [primary_name]
        if fallback_name and fallback_name != primary_name:
            candidates.append(fallback_name)
        if "deterministic" not in candidates:
            candidates.append("deterministic")

        last_error = None
        for prov_name in candidates:
            provider = self.manager.get_provider(prov_name)
            models = provider.get_supported_models()
            model_name = provider_models.get(prov_name, models[0] if models else "default")
            api_key = provider_keys.get(prov_name) or getattr(settings, f"{prov_name.upper()}_API_KEY", None)

            try:
                logger.info(f"AIRouter attempting provider '{prov_name}' (model: {model_name}) for agent '{agent_name}'")
                result = await asyncio.wait_for(
                    provider.generate_text(
                        prompt=sanitized_prompt,
                        system_instruction=sys_inst,
                        model=model_name,
                        api_key=api_key,
                        max_tokens=max_tokens
                    ),
                    timeout=15.0
                )

                # Log usage to DB
                if self.db:
                    cost_usd = calculate_cost_usd(
                        model_name,
                        result.get("prompt_tokens", 0),
                        result.get("completion_tokens", 0)
                    )
                    repo = BusinessRepository(self.db)
                    repo.log_ai_usage({
                        "store_id": store_id,
                        "execution_id": execution_id,
                        "agent_name": agent_name,
                        "provider_name": prov_name,
                        "model_name": model_name,
                        "prompt_tokens": result.get("prompt_tokens", 0),
                        "completion_tokens": result.get("completion_tokens", 0),
                        "total_tokens": result.get("total_tokens", 0),
                        "estimated_cost_usd": cost_usd,
                        "latency_ms": result.get("latency_ms", 0.0),
                        "status": "SUCCESS"
                    })

                return result

            except Exception as e:
                last_error = str(e)
                logger.warning(f"AIRouter: Provider '{prov_name}' failed: {e}. Falling back to next candidate.")
                if self.db:
                    repo = BusinessRepository(self.db)
                    repo.log_ai_usage({
                        "store_id": store_id,
                        "execution_id": execution_id,
                        "agent_name": agent_name,
                        "provider_name": prov_name,
                        "model_name": model_name,
                        "status": "FAILED",
                        "error_message": str(e)
                    })

        # Ultimate fallback to deterministic provider
        det_provider = self.manager.get_provider("deterministic")
        return await det_provider.generate_text(prompt=sanitized_prompt, system_instruction=sys_inst)

    def route_text_generation_sync(
        self,
        prompt: str,
        agent_name: str = "General",
        store_id: str = "STORE_001",
        execution_id: Optional[str] = None,
        max_tokens: int = 800
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for agent nodes and synchronous workflows.
        Executes real LLM calls cleanly across threaded or event-loop environments.
        """
        import concurrent.futures
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        asyncio.run,
                        self.route_text_generation(prompt, agent_name, store_id, execution_id, max_tokens)
                    )
                    return future.result(timeout=20.0)
            else:
                return loop.run_until_complete(
                    self.route_text_generation(prompt, agent_name, store_id, execution_id, max_tokens)
                )
        except Exception:
            return asyncio.run(
                self.route_text_generation(prompt, agent_name, store_id, execution_id, max_tokens)
            )

    async def route_structured_generation(
        self,
        prompt: str,
        agent_name: str = "General",
        store_id: str = "STORE_001",
        execution_id: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes structured JSON generation with fallback:
        Primary -> Fallback -> Deterministic.
        """
        sanitized_prompt = PromptManager.sanitize_untrusted_input(prompt)
        sys_inst = PromptManager.get_system_instruction(agent_name)

        primary_name = "deterministic"
        fallback_name = None
        provider_keys = {}
        provider_models = {}

        if self.db:
            repo = BusinessRepository(self.db)
            db_settings = repo.get_ai_provider_settings(store_id=store_id)
            for s in db_settings:
                if s.api_key:
                    provider_keys[s.provider_name] = s.api_key
                if s.model_name:
                    provider_models[s.provider_name] = s.model_name
                if s.is_primary and s.is_enabled:
                    primary_name = s.provider_name
                elif s.is_fallback and s.is_enabled:
                    fallback_name = s.provider_name

        ai_mode = getattr(settings, "AI_MODE", "deterministic").lower()
        if ai_mode != "deterministic":
            primary_name = ai_mode
        elif getattr(settings, "GEMINI_API_KEY", None):
            primary_name = "gemini"
        elif getattr(settings, "OPENAI_API_KEY", None):
            primary_name = "openai"
        elif getattr(settings, "GROQ_API_KEY", None):
            primary_name = "groq"

        candidates = [primary_name]
        if fallback_name and fallback_name != primary_name:
            candidates.append(fallback_name)
        if "deterministic" not in candidates:
            candidates.append("deterministic")

        for prov_name in candidates:
            provider = self.manager.get_provider(prov_name)
            models = provider.get_supported_models()
            model_name = provider_models.get(prov_name, models[0] if models else "default")
            api_key = provider_keys.get(prov_name) or getattr(settings, f"{prov_name.upper()}_API_KEY", None)

            try:
                result = await asyncio.wait_for(
                    provider.generate_structured(
                        prompt=sanitized_prompt,
                        system_instruction=sys_inst,
                        model=model_name,
                        api_key=api_key,
                        schema=schema
                    ),
                    timeout=15.0
                )

                if self.db:
                    cost_usd = calculate_cost_usd(
                        model_name,
                        result.get("prompt_tokens", 0),
                        result.get("completion_tokens", 0)
                    )
                    repo = BusinessRepository(self.db)
                    repo.log_ai_usage({
                        "store_id": store_id,
                        "execution_id": execution_id,
                        "agent_name": agent_name,
                        "provider_name": prov_name,
                        "model_name": model_name,
                        "prompt_tokens": result.get("prompt_tokens", 0),
                        "completion_tokens": result.get("completion_tokens", 0),
                        "total_tokens": result.get("total_tokens", 0),
                        "estimated_cost_usd": cost_usd,
                        "latency_ms": result.get("latency_ms", 0.0),
                        "status": "SUCCESS"
                    })

                return result
            except Exception as e:
                logger.warning(f"AIRouter structured provider '{prov_name}' failed: {e}. Trying fallback.")

        det_provider = self.manager.get_provider("deterministic")
        return await det_provider.generate_structured(prompt=sanitized_prompt, schema=schema)
