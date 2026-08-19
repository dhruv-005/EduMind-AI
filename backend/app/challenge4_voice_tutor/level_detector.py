import re
from typing import Dict, Any, List
from app.core.logger import logger

# Vocabulary complexity indicators
SIMPLE_WORDS = {
    "what", "how", "why", "is", "are", "the", "a",
    "help", "dont", "understand", "explain", "tell",
    "show", "example", "simple", "easy", "basic"
}

INTERMEDIATE_WORDS = {
    "analyze", "compare", "describe", "relationship",
    "function", "process", "method", "theory",
    "concept", "principle", "factor", "determine"
}

ADVANCED_WORDS = {
    "differentiate", "synthesize", "evaluate",
    "derive", "demonstrate", "formulate", "construct",
    "integrate", "interpret", "extrapolate", "correlate",
    "hypothesis", "paradigm", "phenomenon", "algorithm"
}

# Response complexity by level
RESPONSE_GUIDELINES = {
    "beginner": {
        "vocabulary": "simple everyday words",
        "sentence_length": "short (5-10 words)",
        "examples": "concrete, familiar objects",
        "analogies": "everyday life situations",
        "depth": "surface level explanation"
    },
    "intermediate": {
        "vocabulary": "subject-specific terms with brief explanations",
        "sentence_length": "medium (10-20 words)",
        "examples": "real-world applications",
        "analogies": "relatable scenarios",
        "depth": "conceptual understanding"
    },
    "advanced": {
        "vocabulary": "technical terminology freely",
        "sentence_length": "complex sentences allowed",
        "examples": "abstract and theoretical",
        "analogies": "domain-specific analogies",
        "depth": "deep analysis and connections"
    }
}


class LevelDetector:
    """
    Detect student's academic level from their speech.
    Adjusts tutor response complexity accordingly.
    """

    def analyze_vocabulary_complexity(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Analyze vocabulary complexity of student's text.
        Returns complexity metrics.
        """
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return {
                "complexity": "intermediate",
                "score": 0.5
            }

        simple_count = sum(
            1 for w in words if w in SIMPLE_WORDS
        )
        intermediate_count = sum(
            1 for w in words if w in INTERMEDIATE_WORDS
        )
        advanced_count = sum(
            1 for w in words if w in ADVANCED_WORDS
        )

        total = len(words)
        advanced_ratio = advanced_count / total
        intermediate_ratio = intermediate_count / total

        if advanced_ratio > 0.1:
            complexity = "advanced"
            score = 0.8 + advanced_ratio
        elif intermediate_ratio > 0.1 or advanced_count > 0:
            complexity = "intermediate"
            score = 0.5 + intermediate_ratio
        else:
            complexity = "beginner"
            score = 0.2 + (simple_count / total) * 0.3

        return {
            "complexity": complexity,
            "score": min(round(score, 3), 1.0),
            "word_count": total,
            "advanced_count": advanced_count,
            "intermediate_count": intermediate_count,
            "simple_count": simple_count
        }

    def detect_question_type(self, text: str) -> str:
        """
        Detect type of question asked.
        Returns: conceptual/factual/calculation/procedural
        """
        text_lower = text.lower()

        calculation_patterns = [
            r'\bcalculate\b', r'\bsolve\b', r'\bfind the\b',
            r'\bcompute\b', r'\bhow many\b', r'\bhow much\b',
            r'\bvalue of\b', r'\bequals?\b'
        ]
        for pattern in calculation_patterns:
            if re.search(pattern, text_lower):
                return "calculation"

        conceptual_patterns = [
            r'\bwhy\b', r'\bexplain\b', r'\bhow does\b',
            r'\bwhat is the (reason|cause|effect)\b',
            r'\bwhat happens\b', r'\bwhy does\b'
        ]
        for pattern in conceptual_patterns:
            if re.search(pattern, text_lower):
                return "conceptual"

        procedural_patterns = [
            r'\bhow (to|do)\b', r'\bsteps\b',
            r'\bprocess\b', r'\bprocedure\b', r'\bmethod\b'
        ]
        for pattern in procedural_patterns:
            if re.search(pattern, text_lower):
                return "procedural"

        return "factual"

    def estimate_grade_level(
        self,
        vocabulary_complexity: str,
        avg_words_per_sentence: float
    ) -> str:
        """Estimate grade level from speech patterns."""
        if (
            vocabulary_complexity == "advanced" and
            avg_words_per_sentence > 15
        ):
            return "Grade 11-12 or Higher"
        elif (
            vocabulary_complexity == "intermediate" or
            avg_words_per_sentence > 10
        ):
            return "Grade 7-10"
        else:
            return "Grade 1-6"

    def detect_level(
        self,
        text: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main level detection method.
        Analyzes current text + conversation history.
        Returns detected level with recommendations.
        """
        # Analyze current text
        vocab_analysis = self.analyze_vocabulary_complexity(
            text
        )
        question_type = self.detect_question_type(text)

        # Count words per sentence
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_words = (
            sum(len(s.split()) for s in sentences) /
            max(len(sentences), 1)
        )

        # Also analyze history if available
        history_complexity = "intermediate"
        if conversation_history:
            history_texts = " ".join([
                turn.get("text", "")
                for turn in conversation_history[-5:]
                if turn.get("role") == "student"
            ])
            if history_texts:
                hist_analysis = self.analyze_vocabulary_complexity(
                    history_texts
                )
                history_complexity = hist_analysis["complexity"]

        # Determine final level
        complexity_votes = [
            vocab_analysis["complexity"],
            history_complexity
        ]

        # Majority vote
        from collections import Counter
        level = Counter(complexity_votes).most_common(1)[0][0]

        estimated_grade = self.estimate_grade_level(
            level, avg_words
        )
        guidelines = RESPONSE_GUIDELINES.get(
            level, RESPONSE_GUIDELINES["intermediate"]
        )

        result = {
            "detected_level": level,
            "confidence": vocab_analysis["score"],
            "vocabulary_complexity": (
                vocab_analysis["complexity"]
            ),
            "question_type": question_type,
            "estimated_grade": estimated_grade,
            "avg_words_per_sentence": round(avg_words, 1),
            "recommended_response_level": level,
            "response_guidelines": guidelines
        }

        logger.debug(
            f"Level detected: {level} "
            f"(confidence={vocab_analysis['score']:.2f})"
        )

        return result


# Singleton
level_detector = LevelDetector()
