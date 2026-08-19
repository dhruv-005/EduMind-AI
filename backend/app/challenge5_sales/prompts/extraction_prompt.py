# Version: 1.0.0

INTENT_EXTRACTION_PROMPT = """Analyze customer message and extract:
- Budget (min/max)
- Required features
- Preferred/avoided brands
- Product category
- Urgency level
- Objections raised

Message: {message}
Context: {context}

Return valid JSON only."""

BUDGET_EXTRACTION_PROMPT = """Extract budget from this text:
"{text}"

Return JSON: {{"budget_min": null, "budget_max": null}}
Use numbers only, no currency symbols."""

FEATURE_EXTRACTION_PROMPT = """Extract required product features:
"{text}"

Return JSON array: ["feature1", "feature2"]
Be specific and concise."""
