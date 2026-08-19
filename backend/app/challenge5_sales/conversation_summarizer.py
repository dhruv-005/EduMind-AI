from typing import Dict, Any, List, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client


class ConversationSummarizer:
    """
    Summarize sales conversations.
    Used for escalation handoffs and reporting.
    """

    def format_history_for_prompt(
        self,
        history: List[Dict[str, Any]]
    ) -> str:
        """Format conversation history for LLM prompt."""
        if not history:
            return "No conversation history"

        formatted = []
        for turn in history[-15:]:
            role = turn.get("role", "unknown")
            text = turn.get("text", "")
            if role == "customer":
                formatted.append(f"Customer: {text}")
            else:
                formatted.append(f"AI Sales: {text}")

        return "\n".join(formatted)

    async def summarize(
        self,
        conversation_history: List[Dict[str, Any]],
        requirements: Dict[str, Any],
        lead_score: Dict[str, Any]
    ) -> str:
        """
        Generate conversation summary.
        Returns concise summary for reporting.
        """
        history_text = self.format_history_for_prompt(
            conversation_history
        )

        prompt = f"""Summarize this sales conversation in 3-4 sentences.

Lead Score: {lead_score.get('total_score', 0)}/100
Category: {lead_score.get('category', 'unknown')}

Conversation:
{history_text}

Summary should include:
- What customer wants
- Budget if mentioned
- Key concerns raised
- Current status/next step"""

        try:
            summary = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "Summarize sales conversations concisely. "
                    "Focus on actionable information."
                ),
                max_tokens=200,
                temperature=0.3
            )
            return summary.strip()

        except Exception as e:
            logger.warning(f"Summarization failed: {e}")
            category = requirements.get(
                "category_interest", "products"
            )
            budget = requirements.get("budget_max", "flexible")
            return (
                f"Customer interested in {category} "
                f"with budget of ${budget}. "
                f"Lead score: {lead_score.get('total_score', 0)}/100. "
                f"Status: {lead_score.get('category', 'unknown')}."
            )


# Singleton
conversation_summarizer = ConversationSummarizer()
