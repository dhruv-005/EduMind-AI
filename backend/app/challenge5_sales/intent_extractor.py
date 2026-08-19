import re
import json
from typing import Dict, Any, Optional, List
from app.core.logger import logger
from app.shared.llm_client import llm_client


class IntentExtractor:
    """
    Extract customer intent and requirements from conversation.
    Identifies: budget, features, brands, urgency, objections.
    """

    def extract_budget(
        self,
        text: str
    ) -> Dict[str, Optional[float]]:
        """Extract budget from customer message."""
        text_lower = text.lower()

        # Patterns for budget extraction
        under_patterns = [
            r'under\s*\$?(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'less than\s*\$?(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'below\s*\$?(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'max(?:imum)?\s*\$?(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'budget.*?\$?(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'spend.*?\$?(\d+(?:,\d{3})*(?:\.\d+)?)'
        ]

        range_pattern = (
            r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)'
            r'\s*(?:to|-)\s*'
            r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)'
        )

        budget_min = None
        budget_max = None

        # Check range pattern first
        range_match = re.search(range_pattern, text)
        if range_match:
            try:
                budget_min = float(
                    range_match.group(1).replace(",", "")
                )
                budget_max = float(
                    range_match.group(2).replace(",", "")
                )
                return {
                    "budget_min": budget_min,
                    "budget_max": budget_max
                }
            except ValueError:
                pass

        # Check under/max patterns
        for pattern in under_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    budget_max = float(
                        match.group(1).replace(",", "")
                    )
                    return {
                        "budget_min": None,
                        "budget_max": budget_max
                    }
                except ValueError:
                    pass

        # Check for general price mention
        price_match = re.search(
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?)',
            text
        )
        if price_match:
            try:
                budget_max = float(
                    price_match.group(1).replace(",", "")
                )
                return {
                    "budget_min": None,
                    "budget_max": budget_max * 1.1
                }
            except ValueError:
                pass

        return {"budget_min": None, "budget_max": None}

    def extract_urgency(self, text: str) -> str:
        """Detect purchase urgency from text."""
        text_lower = text.lower()

        high_urgency = [
            "today", "now", "immediately", "urgent",
            "asap", "right away", "this week",
            "need it fast", "as soon as possible",
            "immediately", "emergency"
        ]

        low_urgency = [
            "just browsing", "looking around",
            "not sure yet", "maybe later",
            "thinking about", "someday", "eventually",
            "no rush", "whenever"
        ]

        if any(kw in text_lower for kw in high_urgency):
            return "high"
        elif any(kw in text_lower for kw in low_urgency):
            return "low"
        else:
            return "normal"

    def extract_brands(
        self,
        text: str
    ) -> Dict[str, List[str]]:
        """Extract preferred and avoided brands."""
        text_lower = text.lower()

        # Common brands (expandable)
        known_brands = [
            "apple", "samsung", "sony", "lg", "dell",
            "hp", "lenovo", "asus", "acer", "microsoft",
            "google", "amazon", "nike", "adidas", "honda",
            "toyota", "bmw", "mercedes", "ford", "chevrolet",
            "ikea", "dyson", "bosch", "philips", "panasonic"
        ]

        preferred = []
        avoided = []

        avoid_patterns = [
            r"(?:not|no|avoid|don't want|hate)\s+(\w+)",
            r"(\w+)\s+(?:is bad|sucks|is terrible)"
        ]

        prefer_patterns = [
            r"(?:prefer|like|love|want|looking for)\s+(\w+)",
            r"(\w+)\s+(?:is great|is good|fan of)"
        ]

        for brand in known_brands:
            if brand in text_lower:
                # Check if it's in avoid context
                is_avoided = False
                for pattern in avoid_patterns:
                    matches = re.findall(pattern, text_lower)
                    if brand in matches:
                        is_avoided = True
                        break

                if is_avoided:
                    avoided.append(brand.title())
                else:
                    preferred.append(brand.title())

        return {
            "preferred_brands": preferred,
            "avoided_brands": avoided
        }

    def extract_features(
        self,
        text: str
    ) -> List[str]:
        """Extract required features from text."""
        text_lower = text.lower()
        features = []

        # Feature keywords
        feature_keywords = [
            "long battery", "battery life", "fast",
            "lightweight", "portable", "waterproof",
            "wireless", "bluetooth", "wifi", "4g", "5g",
            "large screen", "small", "compact",
            "high resolution", "4k", "hd", "oled",
            "gaming", "business", "student",
            "storage", "memory", "ram", "ssd", "gpu",
            "noise cancelling", "touch screen",
            "foldable", "dual sim", "good camera"
        ]

        for kw in feature_keywords:
            if kw in text_lower:
                features.append(kw)

        return features

    def detect_objections(
        self,
        text: str
    ) -> List[str]:
        """Detect customer objections."""
        text_lower = text.lower()
        objections = []

        objection_patterns = {
            "price_too_high": [
                "too expensive", "too much", "overpriced",
                "can't afford", "out of my budget",
                "too costly"
            ],
            "not_sure": [
                "not sure", "maybe", "thinking about it",
                "need to think", "not decided"
            ],
            "need_to_compare": [
                "comparing", "looking at others",
                "checking alternatives", "other options"
            ],
            "delivery_concern": [
                "delivery time", "shipping", "how long",
                "when will it arrive"
            ],
            "quality_concern": [
                "good quality", "durable", "reliable",
                "last long", "warranty"
            ]
        }

        for objection_type, keywords in objection_patterns.items():
            if any(kw in text_lower for kw in keywords):
                objections.append(objection_type)

        return objections

    async def extract_with_llm(
        self,
        conversation_text: str
    ) -> Dict[str, Any]:
        """
        Use LLM to extract comprehensive customer intent.
        More accurate than rule-based extraction.
        """
        prompt = f"""Analyze this customer conversation and extract requirements.

Conversation:
{conversation_text[:1500]}

Extract and return JSON:
{{
    "budget_min": null or number,
    "budget_max": null or number,
    "required_features": ["feature1", "feature2"],
    "preferred_brands": ["brand1"],
    "avoided_brands": ["brand2"],
    "category_interest": "product category",
    "urgency": "high/normal/low",
    "objections": ["objection1"],
    "purchase_intent": "high/medium/low",
    "specific_requirements": "any specific needs"
}}

Return ONLY valid JSON."""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are an expert sales analyst. "
                    "Extract customer requirements accurately. "
                    "Return only valid JSON."
                ),
                max_tokens=400,
                temperature=0.1
            )

            json_match = re.search(
                r'\{.+\}',
                response,
                re.DOTALL
            )
            if json_match:
                data = json.loads(json_match.group())
                return data

        except Exception as e:
            logger.warning(f"LLM intent extraction failed: {e}")

        return {}

    async def extract_all(
        self,
        message: str,
        conversation_history: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full intent extraction pipeline.
        Combines rule-based + LLM extraction.
        """
        # Rule-based extraction (fast)
        budget = self.extract_budget(message)
        urgency = self.extract_urgency(message)
        brands = self.extract_brands(message)
        features = self.extract_features(message)
        objections = self.detect_objections(message)

        # LLM extraction (more accurate)
        llm_context = conversation_history or message
        llm_result = await self.extract_with_llm(llm_context)

        # Merge results (LLM takes precedence)
        merged = {
            "budget_min": (
                llm_result.get("budget_min") or
                budget.get("budget_min")
            ),
            "budget_max": (
                llm_result.get("budget_max") or
                budget.get("budget_max")
            ),
            "required_features": list(set(
                features +
                llm_result.get("required_features", [])
            )),
            "preferred_brands": list(set(
                brands.get("preferred_brands", []) +
                llm_result.get("preferred_brands", [])
            )),
            "avoided_brands": list(set(
                brands.get("avoided_brands", []) +
                llm_result.get("avoided_brands", [])
            )),
            "category_interest": llm_result.get(
                "category_interest"
            ),
            "urgency": (
                llm_result.get("urgency") or urgency
            ),
            "objections": list(set(
                objections +
                llm_result.get("objections", [])
            )),
            "purchase_intent": llm_result.get(
                "purchase_intent", "medium"
            ),
            "specific_requirements": llm_result.get(
                "specific_requirements", ""
            )
        }

        logger.debug(
            f"Intent extracted: budget_max={merged['budget_max']} "
            f"urgency={merged['urgency']} "
            f"features={len(merged['required_features'])}"
        )

        return merged


# Singleton
intent_extractor = IntentExtractor()
