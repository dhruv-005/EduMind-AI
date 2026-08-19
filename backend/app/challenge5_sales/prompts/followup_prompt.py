# Version: 1.0.0

EMAIL_FOLLOWUP_PROMPT = """Write a professional sales follow-up email.

Customer: {customer_name}
Interested in: {category}
Budget: {budget}
Top recommendation: {top_product}

Email should:
- Have Subject: line
- Thank customer for interest
- Summarize their needs
- Highlight top recommendation
- Include clear call-to-action
- Be under 200 words

Professional but warm tone."""

WHATSAPP_FOLLOWUP_PROMPT = """Write a WhatsApp follow-up message.

Customer: {customer_name}
Product they liked: {product}

Requirements:
- Casual, friendly tone
- Under 100 words
- Use simple formatting
- Include emoji (1-2 max)
- Clear call-to-action"""

OBJECTION_HANDLER_PROMPT = """Customer raised this objection:
"{objection}"

Context: {context}

Write an empathetic response (2-3 sentences) that:
1. Acknowledges their concern
2. Provides helpful information
3. Guides them forward without pressure"""
