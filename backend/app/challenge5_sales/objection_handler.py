from typing import Dict, Any, List, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client

OBJECTION_RESPONSES = {
    "price_too_high": (
        "I understand budget is important. "
        "Let me show you some great options "
        "that offer excellent value. "
        "We also have flexible payment options available. "
        "What's the best budget range for you?"
    ),
    "not_sure": (
        "That's completely understandable! "
        "Take your time. I can help you compare options "
        "and answer any questions. "
        "What specific features are most important to you?"
    ),
    "need_to_compare": (
        "Smart thinking! Comparing options is always wise. "
        "I can help you with a detailed comparison. "
        "What other products are you considering?"
    ),
    "delivery_concern": (
        "Great question about delivery! "
        "Most of our products ship within 2-3 business days. "
        "Express delivery is also available. "
        "When do you need it by?"
    ),
    "quality_concern": (
        "Quality is our top priority! "
        "All products come with manufacturer warranty. "
        "We also have a satisfaction guarantee. "
        "Would you like to see our top-rated options?"
    )
}


class ObjectionHandler:
    """Handle customer objections with appropriate responses."""

    def get_template_response(
        self,
        objection_type: str
    ) -> str:
        """Get template response for objection type."""
        return OBJECTION_RESPONSES.get(
            objection_type,
            "I understand your concern. "
            "Let me help address that for you. "
            "Could you tell me more about what you're looking for?"
        )

    async def generate_response(
        self,
        objection: str,
        context: str,
        products: List[Dict[str, Any]] = None
    ) -> str:
        """Generate personalized objection response using LLM."""
        products_ctx = ""
        if products:
            products_ctx = (
                f"Available products: " +
                ", ".join([
                    p.get("product_name", "product")
                    for p in products[:3]
                ])
            )

        prompt = f"""A customer raised this objection/concern:
"{objection}"

Context: {context[:300]}
{products_ctx}

Write a helpful, empathetic response (2-3 sentences) that:
1. Acknowledges their concern
2. Addresses it directly
3. Guides them toward a solution
4. Doesn't pressure them

Be friendly and helpful, not pushy."""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are a helpful, empathetic sales assistant. "
                    "Handle objections with understanding. "
                    "Never be pushy or dismissive."
                ),
                max_tokens=150,
                temperature=0.5
            )
            return response.strip()

        except Exception as e:
            logger.warning(
                f"Objection response generation failed: {e}"
            )
            return self.get_template_response("not_sure")

    def detect_and_handle(
        self,
        message: str,
        objections: List[str]
    ) -> Optional[str]:
        """
        Detect if message contains objection and return response.
        Returns None if no objection detected.
        """
        if not objections:
            return None

        # Return template response for first objection
        return self.get_template_response(objections[0])


# Singleton
objection_handler = ObjectionHandler()
