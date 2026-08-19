from typing import Dict, Any, Optional
from datetime import datetime
from app.core.logger import logger
from app.shared.llm_client import llm_client


ESCALATION_TRIGGERS = {
    "hot_lead": "Lead score >= 85, immediate attention needed",
    "angry_customer": "Customer expressing frustration",
    "complex_requirement": "Requirements too complex for AI",
    "enterprise_deal": "Large enterprise purchase indicated",
    "repeat_customer": "Returning customer with purchase history",
    "ai_cannot_answer": "AI lacks information to answer",
    "price_negotiation": "Customer wants to negotiate price"
}


class EscalationManager:
    """
    Manage escalation from AI to human sales rep.
    Detects when escalation needed and prepares handoff.
    """

    def should_escalate(
        self,
        lead_score: Dict[str, Any],
        conversation_turns: int,
        requirements: Dict[str, Any],
        message: str
    ) -> tuple:
        """
        Determine if conversation should escalate to human.
        Returns (should_escalate, reason).
        """
        # Hot lead threshold
        if lead_score.get("total_score", 0) >= 85:
            return True, "hot_lead"

        # Too many turns without resolution
        if conversation_turns >= 10:
            return True, "ai_cannot_answer"

        # Enterprise signals
        enterprise_keywords = [
            "enterprise", "bulk order", "wholesale",
            "multiple units", "company purchase",
            "corporate", "business account", "invoice"
        ]
        if any(
            kw in message.lower()
            for kw in enterprise_keywords
        ):
            return True, "enterprise_deal"

        # Angry customer
        frustration_keywords = [
            "this is ridiculous", "terrible service",
            "worst", "never buying", "complaint",
            "speak to manager", "human agent"
        ]
        if any(
            kw in message.lower()
            for kw in frustration_keywords
        ):
            return True, "angry_customer"

        # Price negotiation
        negotiation_keywords = [
            "can you give me a discount",
            "best price", "negotiate",
            "price match", "lower the price"
        ]
        if any(
            kw in message.lower()
            for kw in negotiation_keywords
        ):
            return True, "price_negotiation"

        return False, ""

    async def prepare_handoff(
        self,
        conversation_id: str,
        conversation_history: str,
        requirements: Dict[str, Any],
        lead_score: Dict[str, Any],
        escalation_reason: str,
        customer_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepare conversation handoff summary for human rep.
        Returns comprehensive briefing.
        """
        prompt = f"""Prepare a sales handoff briefing for a human rep.

Customer: {customer_name or 'Unknown'}
Escalation reason: {escalation_reason}
Lead score: {lead_score.get('total_score', 0)}/100 ({lead_score.get('category', 'unknown')})

Recent conversation:
{conversation_history[:800]}

Customer requirements:
- Budget: ${requirements.get('budget_max', 'not specified')}
- Category: {requirements.get('category_interest', 'not specified')}
- Features: {', '.join(requirements.get('required_features', [])[:5])}
- Urgency: {requirements.get('urgency', 'normal')}
- Objections: {', '.join(requirements.get('objections', [])[:3])}

Write a concise briefing (5-6 bullet points) for the human rep.
Include: customer need, budget, top concerns, recommended approach."""

        try:
            briefing = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are a sales coordinator. "
                    "Write clear, actionable handoff briefs "
                    "for sales representatives."
                ),
                max_tokens=300,
                temperature=0.3
            )

            handoff = {
                "conversation_id": conversation_id,
                "escalation_reason": escalation_reason,
                "reason_description": ESCALATION_TRIGGERS.get(
                    escalation_reason,
                    "Manual escalation"
                ),
                "lead_score": lead_score,
                "customer_name": customer_name,
                "requirements_summary": {
                    "budget_max": requirements.get("budget_max"),
                    "category": requirements.get(
                        "category_interest"
                    ),
                    "urgency": requirements.get("urgency"),
                    "key_features": requirements.get(
                        "required_features", []
                    )[:3],
                    "objections": requirements.get(
                        "objections", []
                    )[:3]
                },
                "rep_briefing": briefing.strip(),
                "priority": (
                    "urgent"
                    if lead_score.get("total_score", 0) >= 80
                    else "normal"
                ),
                "escalated_at": datetime.utcnow().isoformat(),
                "recommended_action": lead_score.get(
                    "next_action", ""
                )
            }

            logger.warning(
                f"Escalation prepared: "
                f"conv={conversation_id} "
                f"reason={escalation_reason} "
                f"score={lead_score.get('total_score')}"
            )

            return handoff

        except Exception as e:
            logger.error(
                f"Handoff preparation failed: {e}"
            )
            return {
                "conversation_id": conversation_id,
                "escalation_reason": escalation_reason,
                "lead_score": lead_score,
                "customer_name": customer_name,
                "rep_briefing": (
                    "Customer needs immediate assistance. "
                    "Please review conversation history."
                ),
                "escalated_at": datetime.utcnow().isoformat()
            }

    def get_escalation_message(
        self,
        reason: str,
        customer_name: Optional[str] = None
    ) -> str:
        """Get customer-facing escalation message."""
        name = customer_name or "there"
        messages = {
            "hot_lead": (
                f"Hi {name}! You're clearly ready to make a "
                f"decision. Let me connect you with our "
                f"specialist who can finalize everything for you!"
            ),
            "angry_customer": (
                f"I sincerely apologize for any frustration. "
                f"Let me connect you with our senior rep "
                f"who can address this immediately."
            ),
            "enterprise_deal": (
                f"For enterprise orders, I'd like to connect "
                f"you with our business solutions team "
                f"who can provide custom pricing and support."
            ),
            "price_negotiation": (
                f"For special pricing, let me connect you "
                f"with our sales manager who has authority "
                f"to discuss custom deals."
            ),
            "ai_cannot_answer": (
                f"I want to make sure you get the best help. "
                f"Let me connect you with one of our "
                f"specialists who can answer all your questions."
            )
        }

        return messages.get(
            reason,
            f"Let me connect you with a specialist "
            f"who can better assist you!"
        )


# Singleton
escalation_manager = EscalationManager()
