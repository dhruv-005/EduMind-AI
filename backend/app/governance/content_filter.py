import re
from typing import Tuple, List, Dict, Any
from app.core.logger import logger
from app.core.constants import CONTENT_BLOCKED, CONTENT_FLAGGED, CONTENT_PASSED

# Blocked words/patterns
BLOCKED_PATTERNS = [
    r'\b(hack|exploit|inject|jailbreak|bypass|override)\b',
    r'\b(ignore previous|ignore all|forget instructions|new instructions)\b',
    r'\b(profanity1|profanity2)\b',  # Add real profanity words here
    r'<script.*?>.*?</script>',
    r'(SELECT|INSERT|UPDATE|DELETE|DROP|UNION).*?(FROM|INTO|TABLE)',
]

# Flagged patterns (warn but allow)
FLAGGED_PATTERNS = [
    r'\b(password|secret|token|api.?key)\b',
    r'\b(personal|private|confidential)\b',
]

# Education-safe topics for voice tutor
EDUCATION_TOPICS = [
    "math", "science", "english", "history", "geography",
    "physics", "chemistry", "biology", "algebra", "geometry",
    "literature", "grammar", "vocabulary", "equation", "formula",
    "theorem", "hypothesis", "experiment", "calculate", "explain",
    "what is", "how does", "why is", "define", "describe",
    "solve", "help me understand", "can you explain", "teach me"
]

NON_EDUCATION_PATTERNS = [
    r'\b(stock|investment|crypto|bitcoin|trading)\b',
    r'\b(relationship|dating|romance|love advice)\b',
    r'\b(politics|election|government|party)\b',
    r'\b(recipe|cooking|food|restaurant)\b',
    r'\b(movie|entertainment|celebrity|gossip)\b',
]


class ContentFilter:
    """Content safety filter for all AI inputs and outputs."""

    def __init__(self):
        self.blocked_patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL)
            for p in BLOCKED_PATTERNS
        ]
        self.flagged_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in FLAGGED_PATTERNS
        ]
        self.non_education_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in NON_EDUCATION_PATTERNS
        ]

    def check_input(self, text: str) -> Tuple[str, str, List[str]]:
        """
        Check input text for safety.
        Returns: (status, reason, matched_patterns)
        Status: 'passed', 'flagged', 'blocked'
        """
        if not text or not text.strip():
            return CONTENT_PASSED, "Empty input", []

        matched = []

        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.search(text):
                matched.append(pattern.pattern)
                logger.warning(f"Blocked content detected: {pattern.pattern}")
                return CONTENT_BLOCKED, "Content violates safety policy", matched

        # Check flagged patterns
        for pattern in self.flagged_patterns:
            if pattern.search(text):
                matched.append(pattern.pattern)

        if matched:
            logger.info(f"Flagged content detected: {matched}")
            return CONTENT_FLAGGED, "Content flagged for review", matched

        return CONTENT_PASSED, "Content passed safety check", []

    def check_output(self, text: str) -> Tuple[str, str, List[str]]:
        """
        Check AI output text for safety.
        Returns: (status, reason, matched_patterns)
        """
        return self.check_input(text)

    def is_educational(self, text: str) -> Tuple[bool, str]:
        """
        Check if text is educational (for voice tutor).
        Returns: (is_educational, reason)
        """
        text_lower = text.lower()

        # Check non-education patterns first
        for pattern in self.non_education_patterns:
            if pattern.search(text_lower):
                return False, "Topic is outside educational scope"

        # Check for education keywords
        for topic in EDUCATION_TOPICS:
            if topic in text_lower:
                return True, "Educational topic detected"

        # Default allow if no non-education patterns matched
        return True, "No restriction found"

    def sanitize_text(self, text: str) -> str:
        """Remove potentially harmful content from text."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove SQL-like patterns
        text = re.sub(
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b',
            '[REMOVED]',
            text,
            flags=re.IGNORECASE
        )
        # Remove script injections
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
        return text.strip()

    def check_pii(self, text: str) -> Dict[str, Any]:
        """Detect personally identifiable information."""
        pii_found = {}

        # Email pattern
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            pii_found["emails"] = len(emails)

        # Phone pattern
        phones = re.findall(r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
        if phones:
            pii_found["phones"] = len(phones)

        # Credit card pattern
        cards = re.findall(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', text)
        if cards:
            pii_found["credit_cards"] = len(cards)

        return pii_found


# Singleton instance
content_filter = ContentFilter()
