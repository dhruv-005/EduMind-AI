from typing import Dict, Any, Optional
from app.challenge1_evaluator.subjects.base_evaluator import BaseEvaluator


class ScienceEvaluator(BaseEvaluator):
    """
    Science-specific evaluator.
    Checks terminology, cause-effect, and scientific accuracy.
    """

    subject_name = "science"

    def build_evaluation_prompt(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: Optional[str] = None
    ) -> str:
        """Science-specific evaluation prompt."""
        level = f"Grade Level: {grade_level}" if grade_level else ""
        return f"""You are an expert science teacher evaluating a student's answer.

{level}
Question: {question}
Reference Answer: {reference_answer[:600]}
Student Answer: {student_answer[:600]}

Evaluate specifically for SCIENCE. Check:
1. correctness: Are scientific facts and concepts accurate?
2. relevance: Are correct scientific principles applied?
3. completeness: Are cause-effect relationships explained?
   Are all parts of the question addressed?
4. clarity: Is correct scientific terminology used?
   Is the explanation logically structured?

Penalize for: incorrect scientific facts, wrong terminology,
missing cause-effect explanations.

Respond ONLY with valid JSON:
{{
    "correctness": 0.0,
    "relevance": 0.0,
    "completeness": 0.0,
    "clarity": 0.0,
    "terminology_correct": true,
    "cause_effect_explained": true,
    "reasoning": "brief explanation"
}}
"""


# Singleton
science_evaluator = ScienceEvaluator()
