import re
from typing import Dict, List, Any, Tuple
from app.core.logger import logger

# Bias indicator words
GENDER_BIAS_WORDS = [
    "he always", "she always", "men are better", "women are worse",
    "boys are smarter", "girls are weaker", "typical girl", "typical boy"
]

CULTURAL_BIAS_WORDS = [
    "those people", "your kind", "people like you",
    "where you come from", "your culture does"
]

STEREOTYPE_PATTERNS = [
    r'\b(all|every|always|never)\s+(men|women|boys|girls|students|teachers)\b',
    r'\b(naturally|obviously|clearly)\s+(worse|better|smarter|dumber)\b',
]

# Inclusive language suggestions
INCLUSIVE_REPLACEMENTS = {
    "mankind": "humanity",
    "policeman": "police officer",
    "fireman": "firefighter",
    "stewardess": "flight attendant",
    "chairman": "chairperson",
    "he or she": "they",
}


class BiasDetector:
    """Detect and report bias in AI-generated content."""

    def __init__(self):
        self.stereotype_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in STEREOTYPE_PATTERNS
        ]

    def check_gender_bias(self, text: str) -> Dict[str, Any]:
        """Check for gender bias in text."""
        text_lower = text.lower()
        found_bias = []

        for bias_phrase in GENDER_BIAS_WORDS:
            if bias_phrase in text_lower:
                found_bias.append(bias_phrase)

        return {
            "has_bias": len(found_bias) > 0,
            "type": "gender_bias",
            "instances": found_bias,
            "severity": "high" if len(found_bias) > 2 else "medium" if found_bias else "none"
        }

    def check_cultural_bias(self, text: str) -> Dict[str, Any]:
        """Check for cultural bias in text."""
        text_lower = text.lower()
        found_bias = []

        for bias_phrase in CULTURAL_BIAS_WORDS:
            if bias_phrase in text_lower:
                found_bias.append(bias_phrase)

        return {
            "has_bias": len(found_bias) > 0,
            "type": "cultural_bias",
            "instances": found_bias,
            "severity": "high" if len(found_bias) > 1 else "medium" if found_bias else "none"
        }

    def check_stereotypes(self, text: str) -> Dict[str, Any]:
        """Check for stereotype reinforcement."""
        found = []

        for pattern in self.stereotype_patterns:
            matches = pattern.findall(text)
            if matches:
                found.extend(matches)

        return {
            "has_bias": len(found) > 0,
            "type": "stereotype",
            "instances": [str(m) for m in found],
            "severity": "high" if len(found) > 2 else "medium" if found else "none"
        }

    def check_inclusive_language(self, text: str) -> Dict[str, Any]:
        """Check for non-inclusive language and suggest replacements."""
        text_lower = text.lower()
        suggestions = {}

        for word, replacement in INCLUSIVE_REPLACEMENTS.items():
            if word in text_lower:
                suggestions[word] = replacement

        return {
            "has_issues": len(suggestions) > 0,
            "suggestions": suggestions
        }

    def full_bias_check(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Run full bias detection on text.
        Returns comprehensive bias report.
        """
        gender_result = self.check_gender_bias(text)
        cultural_result = self.check_cultural_bias(text)
        stereotype_result = self.check_stereotypes(text)
        inclusive_result = self.check_inclusive_language(text)

        has_any_bias = (
            gender_result["has_bias"] or
            cultural_result["has_bias"] or
            stereotype_result["has_bias"]
        )

        severity_scores = {"high": 3, "medium": 2, "low": 1, "none": 0}
        max_severity = max(
            severity_scores.get(gender_result["severity"], 0),
            severity_scores.get(cultural_result["severity"], 0),
            severity_scores.get(stereotype_result["severity"], 0)
        )
        severity_labels = {3: "high", 2: "medium", 1: "low", 0: "none"}
        overall_severity = severity_labels[max_severity]

        if has_any_bias:
            logger.warning(
                f"Bias detected | severity={overall_severity} | "
                f"context={context[:50]}"
            )

        return {
            "has_bias": has_any_bias,
            "overall_severity": overall_severity,
            "bias_types": {
                "gender": gender_result,
                "cultural": cultural_result,
                "stereotype": stereotype_result
            },
            "inclusive_language": inclusive_result,
            "recommendation": self._get_recommendation(overall_severity)
        }

    def _get_recommendation(self, severity: str) -> str:
        """Get recommendation based on severity."""
        recommendations = {
            "high": "Content should be regenerated. High bias risk detected.",
            "medium": "Content flagged for human review before use.",
            "low": "Minor issues found. Consider editing before publishing.",
            "none": "No significant bias detected. Content appears fair."
        }
        return recommendations.get(severity, "Review recommended.")

    def compare_scores_for_bias(
        self,
        scores: List[Dict[str, Any]],
        group_field: str = "group"
    ) -> Dict[str, Any]:
        """
        Compare evaluation scores across groups for statistical bias.
        Used in Challenge 1 evaluation fairness check.
        """
        if not scores:
            return {"bias_detected": False, "message": "No data to analyze"}

        groups = {}
        for score_entry in scores:
            group = score_entry.get(group_field, "unknown")
            score = score_entry.get("score", 0)
            if group not in groups:
                groups[group] = []
            groups[group].append(score)

        group_stats = {}
        for group, group_scores in groups.items():
            avg = sum(group_scores) / len(group_scores)
            group_stats[group] = {
                "count": len(group_scores),
                "average_score": round(avg, 2),
                "min": min(group_scores),
                "max": max(group_scores)
            }

        # Check if any group has significantly different average
        if len(group_stats) < 2:
            return {
                "bias_detected": False,
                "message": "Need at least 2 groups to compare",
                "group_stats": group_stats
            }

        averages = [s["average_score"] for s in group_stats.values()]
        score_range = max(averages) - min(averages)
        bias_detected = score_range > 15  # >15 point difference is significant

        return {
            "bias_detected": bias_detected,
            "score_range": score_range,
            "group_stats": group_stats,
            "message": (
                f"Significant score disparity detected ({score_range:.1f} points)"
                if bias_detected
                else "Scores appear fair across groups"
            )
        }


# Singleton
bias_detector = BiasDetector()
