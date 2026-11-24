"""
DukaanDost AI - Conversational Business Assistant Service
Processes user messages in Hindi, Hinglish, and English using tool-assisted LLM reasoning.
Persists conversation history, retrieves verified evidence, and provides actionable suggestions.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import ChatMessage
from app.ai.tools import AssistantTools
from app.ai.provider_router import AIRouter

logger = logging.getLogger(__name__)

class AssistantService:
    def __init__(self, db: Session, store_id: str = "STORE_001"):
        self.db = db
        self.store_id = store_id
        self.tools = AssistantTools(db, store_id=store_id)
        self.router = AIRouter(db)

    def process_chat_message(self, user_text: str, session_id: str = "SESSION_DEFAULT", language: str = "hi") -> Dict[str, Any]:
        """
        Main conversational pipeline:
        1. Classifies intent & executes restricted deterministic tools.
        2. Injects tool output as ground-truth evidence into LLM prompt.
        3. Generates conversational response via Groq / active AI provider in requested language (Hindi/English).
        4. Persists message and response into SQLite chat_messages table.
        """
        u_lower = user_text.lower()
        tools_executed = []
        evidence = {}
        suggested_actions = []

        is_english = language.lower() in ["en", "english"] or any(w in u_lower for w in ["in english", "english please"])

        # Intent Recognition & Tool Dispatch
        if any(w in u_lower for w in ["sale", "bikri", "aaj kitni", "today", "yesterday", "revenue"]):
            sales_data = self.tools.get_sales_summary()
            tools_executed.append("get_sales_summary")
            evidence["sales"] = sales_data
            suggested_actions = ["Profit summary dikhao", "Top selling products kya hain?", "Low stock check karo"]

        elif any(w in u_lower for w in ["profit", "income", "margin", "kamai", "fayda", "munafa"]):
            profit_data = self.tools.get_profit_summary()
            tools_executed.append("get_profit_summary")
            evidence["profit"] = profit_data
            suggested_actions = ["Profit ₹2,000 kaise badhayein?", "Sabse bada expense kya hai?", "Breakfast combo check karo"]

        elif any(w in u_lower for w in ["stock", "inventory", "reorder", "khatam", "expiry", "paneer", "mal"]):
            inv_data = self.tools.get_inventory_alerts()
            tools_executed.append("get_inventory_alerts")
            evidence["inventory"] = inv_data
            suggested_actions = ["Expiring stock liquidate karo", "Top sellers restock karo", "Full inventory check karo"]

        elif any(w in u_lower for w in ["customer", "grahak", "inactive", "dormant", "churn", "khate"]):
            cust_data = self.tools.get_customer_segments()
            tools_executed.append("get_customer_segments")
            evidence["customers"] = cust_data
            suggested_actions = ["Inactive customers ko voucher bhejo", "Top customers list", "Today sales"]

        elif any(w in u_lower for w in ["top", "selling", "slow", "product", "item", "sabse jyada"]):
            prod_data = self.tools.get_product_performance()
            tools_executed.append("get_product_performance")
            evidence["products"] = prod_data
            suggested_actions = ["Slow movers discount karo", "Breakfast combo launch karo", "Sales summary"]

        elif any(w in u_lower for w in ["expense", "kharcha", "rent", "bijli", "wages", "bada kharcha"]):
            exp_data = self.tools.get_expense_summary()
            tools_executed.append("get_expense_summary")
            evidence["expenses"] = exp_data
            suggested_actions = ["Net profit kitna bacha?", "Profit ₹2,000 badhane ka plan", "Inventory alerts"]

        elif any(w in u_lower for w in ["campaign", "offer", "voucher", "whatsapp", "message", "prachar", "marketing"]):
            camp_data = self.tools.generate_marketing_draft(offer_description="Breakfast Combo & Daily Staples", discount_pct=5.2)
            tools_executed.append("generate_marketing_draft")
            evidence["marketing"] = camp_data
            suggested_actions = ["Campaign approve karo", "Inactive customers ko bhejo", "Pricing check karo"]

        elif any(w in u_lower for w in ["strategy", "goal", "increase", "badhayein", "plan", "2000", "growth", "tarkki"]):
            strat_data = self.tools.create_growth_strategy("Increase monthly profit by ₹2,000")
            tools_executed.append("create_growth_strategy")
            evidence["strategy"] = strat_data
            suggested_actions = ["Start AI Worker run", "Breakfast combo details", "View approvals"]

        else:
            # General query - pull brief overview
            sales_data = self.tools.get_sales_summary()
            tools_executed.append("get_sales_summary")
            evidence["overview"] = sales_data
            suggested_actions = ["Aaj ki sales kitni hui?", "Is month ka profit?", "Low stock alerts dikhao"]

        # Formulate LLM Prompt with verified ground-truth evidence
        evidence_str = json.dumps(evidence, indent=2)

        if is_english:
            llm_prompt = (
                f"User Question: '{user_text}'\n\n"
                f"Verified Store Records Evidence (Ground Truth):\n{evidence_str}\n\n"
                f"Instructions:\n"
                f"1. Respond directly to Sharma Ji in professional, polite, and natural conversational English.\n"
                f"2. Use exact numbers from the verified evidence above. Never invent fake metrics.\n"
                f"3. Always write monetary amounts with '₹' and 'Rupees' (e.g. '₹4,750 (4,750 Rupees)').\n"
                f"4. Keep the tone warm, respectful, and business-focused for an Indian Kirana shop owner.\n"
                f"5. Keep the answer concise (2-4 crisp sentences)."
            )
        else:
            llm_prompt = (
                f"User Question: '{user_text}'\n\n"
                f"Verified Store Records Evidence (Ground Truth):\n{evidence_str}\n\n"
                f"Instructions:\n"
                f"1. Respond directly to Sharma Ji in polite, natural conversational Hindi (using Devanagari script, e.g. 'नमस्ते शर्मा जी!...').\n"
                f"2. Use exact numbers from the verified evidence above. Never invent fake metrics.\n"
                f"3. Always write monetary amounts with 'रुपये' (e.g. '4,750 रुपये') so speech synthesis sounds natural.\n"
                f"4. Keep the tone warm, respectful, and action-oriented for an Indian Kirana shop owner.\n"
                f"5. Keep the answer concise (2-4 crisp sentences)."
            )

        # Call AI Router (Groq Cloud active)
        ai_response = self.router.route_text_generation_sync(
            prompt=llm_prompt,
            agent_name="Conversational Assistant",
            store_id=self.store_id
        )

        response_text = ai_response.get("text", "Namaste Sharma Ji! Aapki dukan ke verified records fetch ho gaye hain.")

        # Persist User Message
        user_msg = ChatMessage(
            store_id=self.store_id,
            session_id=session_id,
            role="user",
            content=user_text,
            language="hinglish"
        )
        self.db.add(user_msg)

        # Persist Assistant Response
        assistant_msg = ChatMessage(
            store_id=self.store_id,
            session_id=session_id,
            role="assistant",
            content=response_text,
            language="hinglish",
            tools_used=json.dumps(tools_executed),
            evidence_json=json.dumps(evidence),
            suggested_actions=json.dumps(suggested_actions)
        )
        self.db.add(assistant_msg)
        self.db.commit()

        return {
            "role": "assistant",
            "content": response_text,
            "tools_used": tools_executed,
            "evidence": evidence,
            "suggested_actions": suggested_actions,
            "provider": ai_response.get("provider", "groq"),
            "model": ai_response.get("model", "qwen/qwen3.8-27b"),
            "latency_ms": ai_response.get("latency_ms", 0.0)
        }

    def get_chat_history(self, session_id: str = "SESSION_DEFAULT", limit: int = 30) -> List[Dict[str, Any]]:
        """Retrieves chronological conversation history for the session."""
        msgs = (
            self.db.query(ChatMessage)
            .filter_by(store_id=self.store_id, session_id=session_id)
            .order_by(desc(ChatMessage.id))
            .limit(limit)
            .all()
        )
        msgs.reverse()
        result = []
        for m in msgs:
            tools = json.loads(m.tools_used) if m.tools_used else []
            evidence = json.loads(m.evidence_json) if m.evidence_json else {}
            suggestions = json.loads(m.suggested_actions) if m.suggested_actions else []
            result.append({
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "tools_used": tools,
                "evidence": evidence,
                "suggested_actions": suggestions,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None
            })
        return result

    def clear_chat_history(self, session_id: str = "SESSION_DEFAULT") -> int:
        """Clears chat messages for the session."""
        deleted = (
            self.db.query(ChatMessage)
            .filter_by(store_id=self.store_id, session_id=session_id)
            .delete()
        )
        self.db.commit()
        return deleted
