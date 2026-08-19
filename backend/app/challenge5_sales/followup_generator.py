from typing import Dict, Any, List, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client


class FollowUpGenerator:
    """
    Generate professional follow-up content.
    Creates email and WhatsApp messages for sales reps.
    """

    async def generate_email(
        self,
        customer_name: Optional[str],
        recommendations: List[Dict[str, Any]],
        requirements: Dict[str, Any],
        lead_score: Dict[str, Any],
        custom_note: Optional[str] = None
    ) -> str:
        """Generate professional follow-up email."""
        name = customer_name or "Valued Customer"
        budget_ctx = (
            f"${requirements.get('budget_max', 'flexible')}"
        )
        category = requirements.get(
            "category_interest", "products"
        )

        products_text = "\n".join([
            f"• {p.get('product_name', 'Product')} - "
            f"${p.get('product_price', 'Contact for price')}"
            for p in recommendations[:3]
        ])

        prompt = f"""Write a professional sales follow-up email.

Customer: {name}
Budget: {budget_ctx}
Interested in: {category}
Lead category: {lead_score.get('category', 'warm')}

Recommended products:
{products_text}

Custom note from rep: {custom_note or 'None'}

Write a professional, warm email that:
1. Thanks them for their interest
2. Summarizes their requirements
3. Highlights top recommended product
4. Includes clear call-to-action
5. Offers to answer questions

Format with Subject: line first, then email body.
Keep it under 200 words. Professional but friendly tone."""

        try:
            email = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are an expert sales copywriter. "
                    "Write compelling, professional emails "
                    "that convert leads to customers."
                ),
                max_tokens=400,
                temperature=0.6
            )
            return email.strip()

        except Exception as e:
            logger.warning(
                f"Email generation failed: {e}"
            )
            return self._template_email(
                name, category, recommendations
            )

    async def generate_whatsapp(
        self,
        customer_name: Optional[str],
        recommendations: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> str:
        """Generate WhatsApp follow-up message."""
        name = customer_name or "there"
        category = requirements.get(
            "category_interest", "products"
        )

        top_product = recommendations[0] if recommendations else {}
        product_name = top_product.get(
            "product_name", "our top pick"
        )
        product_price = top_product.get(
            "product_price", "competitive price"
        )

        prompt = f"""Write a WhatsApp follow-up message.

Customer: {name}
Interested in: {category}
Top recommended: {product_name} at ${product_price}

Write a short (3-4 sentences), casual WhatsApp message that:
1. Greets them by name
2. References what they were looking for
3. Mentions the top recommendation
4. Asks if they want more info

Use WhatsApp-friendly formatting. No formal email structure.
Casual but professional. Max 100 words."""

        try:
            message = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "Write friendly, conversational "
                    "WhatsApp messages for sales follow-up."
                ),
                max_tokens=150,
                temperature=0.7
            )
            return message.strip()

        except Exception as e:
            logger.warning(
                f"WhatsApp generation failed: {e}"
            )
            return (
                f"Hi {name}! 👋 Thanks for your interest "
                f"in {category}. "
                f"I found some great options for you, "
                f"especially {product_name}. "
                f"Would you like more details? 😊"
            )

    def _template_email(
        self,
        name: str,
        category: str,
        recommendations: List[Dict]
    ) -> str:
        """Template email fallback."""
        products = "\n".join([
            f"• {p.get('product_name', 'Product')}"
            for p in recommendations[:3]
        ])

        return f"""Subject: Your Personalized {category.title()} Recommendations

Dear {name},

Thank you for your interest! Based on your requirements,
I've curated these recommendations for you:

{products}

I'd love to help you find the perfect solution.
Please don't hesitate to reply to this email or
call us directly to discuss your needs.

Best regards,
Sales Team"""

    async def generate_both(
        self,
        customer_name: Optional[str],
        recommendations: List[Dict[str, Any]],
        requirements: Dict[str, Any],
        lead_score: Dict[str, Any],
        custom_note: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate both email and WhatsApp messages."""
        email = await self.generate_email(
            customer_name=customer_name,
            recommendations=recommendations,
            requirements=requirements,
            lead_score=lead_score,
            custom_note=custom_note
        )

        whatsapp = await self.generate_whatsapp(
            customer_name=customer_name,
            recommendations=recommendations,
            requirements=requirements
        )

        return {
            "email": email,
            "whatsapp": whatsapp
        }


# Singleton
followup_generator = FollowUpGenerator()
