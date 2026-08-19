from typing import Dict, Any, Optional, List
from app.core.logger import logger
from app.shared.llm_client import llm_client


class HintEngine:
    """
    Socratic hint engine for voice tutor.
    Guides students to answers instead of giving them directly.
    Uses scaffolded hints: broad → specific → answer.
    """

    HINT_LEVELS = ["broad", "specific", "direct"]

    def __init__(self):
        self._hint_history: Dict[str, List[str]] = {}

    def get_hint_level(
        self,
        session_id: str,
        question_key: str
    ) -> int:
        """
        Get current hint level for a question.
        Returns 0 (broad), 1 (specific), 2 (direct).
        """
        key = f"{session_id}:{question_key}"
        hints_given = self._hint_history.get(key, [])
        return min(len(hints_given), 2)

    def record_hint_given(
        self,
        session_id: str,
        question_key: str,
        hint: str
    ):
        """Record that a hint was given for tracking."""
        key = f"{session_id}:{question_key}"
        if key not in self._hint_history:
            self._hint_history[key] = []
        self._hint_history[key].append(hint)

    async def generate_hint(
        self,
        question: str,
        student_attempt: str,
        subject: str,
        hint_level: int = 0,
        grade_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a scaffolded hint for the student.
        hint_level: 0=broad, 1=specific, 2=direct answer
        """
        level_ctx = (
            f"Grade Level: {grade_level}" if grade_level else ""
        )
        hint_instructions = {
            0: (
                "Give a BROAD hint. Ask a guiding question "
                "that points toward the concept. "
                "DO NOT give the answer. "
                "Maximum 2 sentences."
            ),
            1: (
                "Give a SPECIFIC hint. Point to the exact "
                "concept or formula needed. "
                "Still don't give the full answer. "
                "Maximum 3 sentences."
            ),
            2: (
                "Now explain the complete answer clearly "
                "since the student has tried multiple times. "
                "Show the steps and explain why. "
                "Maximum 5 sentences."
            )
        }

        hint_type = self.HINT_LEVELS[min(hint_level, 2)]
        instruction = hint_instructions[min(hint_level, 2)]

        prompt = f"""A student needs help with this {subject} question.

{level_ctx}
Question: {question}
Student's attempt: {student_attempt}

{instruction}

Your hint (speak naturally as a tutor):"""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    f"You are a patient {subject} tutor. "
                    "Use the Socratic method to guide students "
                    "to discover answers themselves. "
                    "Be encouraging and supportive."
                ),
                max_tokens=200,
                temperature=0.5
            )

            return {
                "hint": response.strip(),
                "hint_level": hint_level,
                "hint_type": hint_type,
                "has_more_hints": hint_level < 2
            }

        except Exception as e:
            logger.warning(f"Hint generation failed: {e}")
            return self._fallback_hint(
                hint_level, subject
            )

    def _fallback_hint(
        self,
        hint_level: int,
        subject: str
    ) -> Dict[str, Any]:
        """Generate template hint when LLM fails."""
        hints = {
            0: (
                f"Think about the core {subject} concepts "
                "related to this question. "
                "What do you already know about this topic?"
            ),
            1: (
                "Try breaking the problem into smaller parts. "
                "What is the first step you would take?"
            ),
            2: (
                "Let me walk you through this step by step. "
                "First, identify what is given. "
                "Then apply the relevant concept or formula."
            )
        }
        level = min(hint_level, 2)
        return {
            "hint": hints[level],
            "hint_level": hint_level,
            "hint_type": self.HINT_LEVELS[level],
            "has_more_hints": level < 2
        }

    async def generate_socratic_question(
        self,
        topic: str,
        student_response: str,
        subject: str
    ) -> str:
        """
        Generate a Socratic follow-up question.
        Deepens understanding through questioning.
        """
        prompt = f"""The student just said: "{student_response}"

Topic: {topic}
Subject: {subject}

Generate ONE thoughtful follow-up question that:
1. Builds on what they said
2. Deepens their understanding
3. Makes them think more deeply
4. Is encouraging and curious in tone

Just the question, nothing else:"""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are a Socratic tutor. "
                    "Ask questions that make students "
                    "think deeper, not just recall facts."
                ),
                max_tokens=100,
                temperature=0.6
            )
            return response.strip()

        except Exception as e:
            logger.warning(
                f"Socratic question generation failed: {e}"
            )
            return (
                "That's interesting! Can you tell me more "
                "about why you think that?"
            )

    def should_use_hint_mode(
        self,
        student_text: str
    ) -> bool:
        """
        Detect if student is struggling and needs hints.
        Returns True if hint mode should activate.
        """
        struggle_indicators = [
            "i don't know", "i dont know",
            "i'm stuck", "im stuck",
            "i don't understand", "i dont understand",
            "help me", "i give up", "too hard",
            "what is the answer", "just tell me",
            "i have no idea", "not sure"
        ]
        text_lower = student_text.lower()
        return any(
            indicator in text_lower
            for indicator in struggle_indicators
        )


# Singleton
hint_engine = HintEngine()
