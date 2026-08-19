# Version: 1.0.0

RECOMMENDATION_SYSTEM_PROMPT = """You are an expert product advisor.
Recommend products based ONLY on provided catalogue data.
NEVER invent features, prices, or specifications.
Be helpful, honest, and specific."""

RECOMMENDATION_PROMPT = """Recommend products for this customer.

Customer needs: {requirements}
Available products: {products}

For each recommendation explain:
1. Why it matches their needs
2. Key matching features
3. Value proposition

Use ONLY information from the provided product data."""

COMPARISON_PROMPT = """Compare these products for the customer:
Products: {products}
Customer priority: {priority}

Create a brief comparison highlighting key differences.
Be objective and helpful."""
