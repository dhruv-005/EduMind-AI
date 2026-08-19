import re
from typing import Dict, Any, Optional, Tuple
from app.core.logger import logger
from app.governance.content_filter import content_filter

# Educational topics and keywords
EDUCATIONAL_KEYWORDS = [
    "explain", "define", "what is", "how does", "why",
    "calculate", "solve", "find", "prove", "describe",
    "compare", "analyze", "summarize", "example",
    "formula", "equation", "theorem", "concept", "theory",
    "learn", "understand", "study", "question", "answer",
    "math", "science", "english", "history", "geography",
    "physics", "chemistry", "biology", "algebra", "geometry",
    "calculus", "grammar", "literature", "vocabulary",
    "photosynthesis", "evolution", "gravity", "atom",
    "cell", "molecule", "energy", "force", "motion",
    "derivative", "integral", "probability", "statistics",
    "help me", "i dont understand", "can you explain",
    "teach me", "show me", "practice", "exercise"
]

# Non-educational topics to reject
NON_EDUCATIONAL_KEYWORDS = [
    "stock market", "cryptocurrency", "bitcoin",
    "relationship advice", "dating", "romance",
    "politics", "election", "vote", "party",
    "movie review", "celebrity gossip", "entertainment",
    "recipe", "cooking", "restaurant",
    "sports betting", "gambling", "casino",
    "illegal", "hack", "cheat", "bypass",
    "generate code for me", "write my essay",
    "do my homework for me completely"
]

REJECTION_MESSAGES = {
    "off_topic": (
        "I'm your educational tutor and I can only help "
        "with academic subjects like math, science, "
        "english, and more. What subject would you "
        "like to study today?"
    ),
    "harmful": (
        "I cannot help with that request. "
        "I'm here to help you learn! "
        "What subject can I teach you today?"
    ),
    "homework_cheating": (
        "I notice you want me to complete your work for you. "
        "Instead, let me guide you through the concepts "
        "so you can solve it yourself! "
        "What part are you struggling with?"
    )
}


class TopicGuard:
    """
    Guard to ensure voice tutor stays on educational topics.
    Rejects non-educational queries with helpful messages.
    """

    def is_educational(
        self,
        text: str
    ) -> Tuple[bool, float, str]:
        """
        Check if text is an educational query.
        Returns (is_educational, confidence, reason).
        """
        text_lower = text.lower().strip()

        if not text_lower:
            return True, 0.5, "empty_input"

        # Check content filter first
        is_edu, reason = content_filter.is_educational(text)
        if not is_edu:
            return False, 0.9, reason

        # Check non-educational keywords
        non_edu_matches = [
            kw for kw in NON_EDUCATIONAL_KEYWORDS
            if kw in text_lower
        ]
        if non_edu_matches:
            return False, 0.85, f"non_educational: {non_edu_matches[0]}"

        # Check educational keywords
        edu_matches = [
            kw for kw in EDUCATIONAL_KEYWORDS
            if kw in text_lower
        ]
        if edu_matches:
            confidence = min(0.5 + len(edu_matches) * 0.1, 0.99)
            return True, confidence, f"educational: {edu_matches[0]}"

        # Check for question patterns
        question_patterns = [
            r'\?$',
            r'^(what|how|why|when|where|who|which|can)\b',
            r'^(is|are|was|were|do|does|did|will|would)\b'
        ]
        for pattern in question_patterns:
            if re.search(pattern, text_lower):
                return True, 0.65, "question_pattern"

        # Default: allow with low confidence
        return True, 0.55, "default_allow"

    def detect_homework_cheating(self, text: str) -> bool:
        """Detect if student wants AI to do homework for them."""
        text_lower = text.lower()
        cheating_patterns = [
            r'do my homework',
            r'write my (essay|report|assignment)',
            r'complete my (assignment|work|task)',
            r'give me all the answers',
            r'just tell me the answer',
            r'do this for me'
        ]
        for pattern in cheating_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def get_rejection_message(
        self,
        reason: str
    ) -> str:
        """Get appropriate rejection message."""
        if "harmful" in reason or "blocked" in reason:
            return REJECTION_MESSAGES["harmful"]
        elif "homework" in reason or "cheating" in reason:
            return REJECTION_MESSAGES["homework_cheating"]
        else:
            return REJECTION_MESSAGES["off_topic"]

    async def check(
        self,
        text: str,
        session_subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full topic guard check.
        Returns check result with recommendation.
        """
        # Check for cheating
        is_cheating = self.detect_homework_cheating(text)
        if is_cheating:
            return {
                "is_educational": False,
                "confidence": 0.95,
                "detected_topic": "homework_cheating",
                "reason": "homework_cheating",
                "should_reject": True,
                "rejection_message": (
                    REJECTION_MESSAGES["homework_cheating"]
                ),
                "hint_mode": True
            }

        # Check educational content
        is_edu, confidence, reason = self.is_educational(text)

        if not is_edu:
            return {
                "is_educational": False,
                "confidence": confidence,
                "detected_topic": None,
                "reason": reason,
                "should_reject": True,
                "rejection_message": self.get_rejection_message(
                    reason
                ),
                "hint_mode": False
            }

        # Detect topic
        detected_topic = self._detect_topic(
            text, session_subject
        )

        return {
            "is_educational": True,
            "confidence": confidence,
            "detected_topic": detected_topic,
            "reason": reason,
            "should_reject": False,
            "rejection_message": None,
            "hint_mode": False
        }

    def _detect_topic(
        self,
        text: str,
        session_subject: Optional[str] = None
    ) -> str:
        """Detect the educational topic from text."""
        text_lower = text.lower()

        topic_map = {
            "mathematics": [
                "math", "algebra", "calculus", "geometry",
                "equation", "formula", "calculate", "solve",
                "derivative", "integral", "probability"
            ],
            "physics": [
                "force", "gravity", "motion", "velocity",
                "acceleration", "energy", "power", "newton",
                "wave", "light", "electricity"
            ],
            "chemistry": [
                "atom", "molecule", "reaction", "element",
                "compound", "acid", "base", "bond",
                "oxidation", "reduction", "periodic"
            ],
            "biology": [
                "cell", "dna", "evolution", "organism",
                "photosynthesis", "mitosis", "protein",
                "ecosystem", "genetics", "chromosome"
            ],
            "english": [
                "grammar", "poem", "essay", "sentence",
                "verb", "noun", "adjective", "literature",
                "writing", "paragraph", "vocabulary"
            ],
            "history": [
                "war", "revolution", "empire", "civilization",
                "century", "historical", "ancient", "modern"
            ]
        }

        for subject, keywords in topic_map.items():
            if any(kw in text_lower for kw in keywords):
                return subject

        return session_subject or "general"


# Singleton
topic_guard = TopicGuard()
