from typing import Dict, Any, Optional
from app.challenge1_evaluator.subjects.base_evaluator import BaseEvaluator


class GeneralEvaluator(BaseEvaluator):
    """
    General subject evaluator.
    Used for history, geography, general knowledge, etc.
    """

    subject_name = "general"

    def build_evaluation_prompt(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: Optional[str] = None
    ) -> str:
        """General evaluation prompt."""
        level = f"Grade Level: {grade_level}" if grade_level else ""
        return f"""You are an expert teacher evaluating a student's answer.

{level}
Question: {question}
Reference Answer: {reference_answer[:600]}
Student Answer: {student_answer[:600]}

Evaluate the student's answer. Check:
1. correctness: Are the key facts and information correct?
2. relevance: Is the answer relevant to the question?
3. completeness: Are all key points covered?
4. clarity: Is the answer clearly and logically presented?

Respond ONLY with valid JSON:
{{
    "correctness": 0.0,
    "relevance": 0.0,
    "completeness": 0.0,
    "clarity": 0.0,
    "reasoning": "brief explanation"
}}
"""


# Singleton
general_evaluator = GeneralEvaluator()
