from typing import Dict, Any, Optional
from app.challenge1_evaluator.subjects.base_evaluator import BaseEvaluator


class EnglishEvaluator(BaseEvaluator):
    """
    English-specific evaluator.
    Checks grammar, coherence, argument quality.
    """

    subject_name = "english"

    def build_evaluation_prompt(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: Optional[str] = None
    ) -> str:
        """English-specific evaluation prompt."""
        level = f"Grade Level: {grade_level}" if grade_level else ""
        return f"""You are an expert English teacher evaluating a student's answer.

{level}
Question: {question}
Reference Answer: {reference_answer[:600]}
Student Answer: {student_answer[:600]}

Evaluate specifically for ENGLISH. Check:
1. correctness: Is the content/interpretation correct?
   Are literary terms used correctly?
2. relevance: Does the answer address the specific question?
3. completeness: Are all required points covered?
   Is there sufficient evidence/examples?
4. clarity: Is grammar correct? Is writing coherent?
   Is the argument well-structured?

Respond ONLY with valid JSON:
{{
    "correctness": 0.0,
    "relevance": 0.0,
    "completeness": 0.0,
    "clarity": 0.0,
    "grammar_quality": 0.0,
    "argument_strength": 0.0,
    "reasoning": "brief explanation"
}}
"""


# Singleton
english_evaluator = EnglishEvaluator()
