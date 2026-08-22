import re
from typing import Dict, Any, List
from app.core.logger import logger


class BiasDetector:
    """Pillar 4: Bias Detection & Fairness."""

    def __init__(self):
        self.bias_patterns = {
            "gender": [
                r"\b(man's job|woman's job|housewife|chairman|stewardess|mankind)\b",
                r"\b(emotional female|aggressive male|girls can't|boys don't)\b"
            ],
            "racial_ethnic": [
                r"\b(superior race|inferior race|illegal alien|exotic looking)\b"
            ],
            "general_bias": [
                r"\b(backward people|uncivilized|primitive culture)\b"
            ]
        }

    def scan_text(self, text: str) -> Dict[str, Any]:
        """Scan text for potential bias."""
        if not text:
            return {"has_bias": False, "detected_categories": [], "details": [], "bias_score": 0.0}

        text_lower = text.lower()
        detected = []
        details = []

        for category, patterns in self.bias_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    detected.append(category)
                    details.append(f"Potential {category} bias: {', '.join(matches)}")

        has_bias = len(detected) > 0
        if has_bias:
            logger.warning(f"Bias detected: {detected}")

        return {
            "has_bias": has_bias,
            "detected_categories": list(set(detected)),
            "details": details,
            "bias_score": round(0.95 if has_bias else 0.05, 2)
        }

    def detect_bias(self, text: str) -> Dict[str, Any]:
        """Alias for scan_text."""
        return self.scan_text(text)

    def check(self, text: str) -> Dict[str, Any]:
        """Alias for scan_text."""
        return self.scan_text(text)


bias_detector = BiasDetector()
