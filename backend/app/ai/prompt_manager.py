import re
from typing import Optional

class PromptManager:
    """
    Manages structured prompts, system instructions, and input sanitization
    against prompt injection attacks.
    """

    # Patterns commonly used in prompt injection attempts
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"system\s*prompt",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"jailbreak",
        r"bypass\s+safety",
        r"disregard\s+the\s+above"
    ]

    @classmethod
    def sanitize_untrusted_input(cls, text: str) -> str:
        """
        Sanitizes untrusted text (customer names, descriptions, notes)
        to prevent prompt injection into LLM system context.
        """
        if not text:
            return ""

        cleaned = text.strip()
        for pat in cls.INJECTION_PATTERNS:
            cleaned = re.sub(pat, "[FILTERED_INSTRUCTION]", cleaned, flags=re.IGNORECASE)

        # Enforce maximum safe length
        return cleaned[:2000]

    @classmethod
    def get_system_instruction(cls, agent_name: str) -> str:
        base = (
            "You are DukaanDost AI, an autonomous AI business partner assisting Sharma Ji "
            "with Sharma General Store in Ranchi, Jharkhand, India. "
            "Guiding principle: Deliver practical, respectful Kirana growth insights. "
            "Always preserve strict financial accuracy. Never invent fictitious transaction totals. "
            "Bilingual capability: Respond fluently in conversational Hindi and English."
        )

        agent_roles = {
            "Business Analyst": "Focus on sales patterns, customer churn, and explaining margin health.",
            "Strategy Planner": "Formulate 4 concrete initiatives to close the ₹2,000 monthly income gap.",
            "Marketing Agent": "Draft compelling localized promotional messages for customer segments (combos, reactivation).",
            "Inventory Agent": "Recommend stock reorder thresholds, expiry markdown timing, and waste elimination.",
            "Finance Agent": "Enforce strict margin validation, never allow selling below cost, cap discounts at 15%.",
            "Supervisor": "Coordinate workflow progression, assign tasks, and monitor business outcomes."
        }

        role_desc = agent_roles.get(agent_name, "Assist the Kirana store with actionable recommendations.")
        return f"{base}\nAgent Role ({agent_name}): {role_desc}"
