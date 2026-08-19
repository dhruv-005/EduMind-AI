import re
from typing import Dict, Any, Optional
from app.challenge1_evaluator.subjects.base_evaluator import BaseEvaluator
from app.core.logger import logger


class MathEvaluator(BaseEvaluator):
    """
    Math-specific evaluator.
    Checks formulas, steps, numerical answers, and units.
    """

    subject_name = "mathematics"

    def build_evaluation_prompt(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: Optional[str] = None
    ) -> str:
        """Math-specific evaluation prompt."""
        level = f"Grade Level: {grade_level}" if grade_level else ""
        return f"""You are an expert mathematics teacher evaluating a student's answer.

{level}
Question: {question}
Reference Answer: {reference_answer[:600]}
Student Answer: {student_answer[:600]}

Evaluate specifically for MATHEMATICS. Check:
1. correctness: Is the final answer correct? Are formulas right?
2. relevance: Did the student use the right approach/method?
3. completeness: Are all steps shown? Are units included?
4. clarity: Is the working clearly presented step by step?

Important: Award partial credit for correct method even if final answer is wrong.
Penalize heavily if: wrong formula used, no working shown for complex problems.

Respond ONLY with valid JSON:
{{
    "correctness": 0.0,
    "relevance": 0.0,
    "completeness": 0.0,
    "clarity": 0.0,
    "correct_formula": true,
    "steps_shown": true,
    "units_correct": true,
    "reasoning": "brief explanation"
}}
"""

    def check_numerical_answer(
        self,
        student_answer: str,
        reference_answer: str
    ) -> Dict[str, Any]:
        """
        Check if numerical answers match.
        Handles approximate equality for floating point numbers.
        """
        # Extract numbers from both answers
        student_nums = re.findall(
            r'-?\d+\.?\d*',
            student_answer
        )
        reference_nums = re.findall(
            r'-?\d+\.?\d*',
            reference_answer
        )

        if not student_nums or not reference_nums:
            return {
                "numerical_match": False,
                "student_number": None,
                "reference_number": None
            }

        try:
            student_val = float(student_nums[-1])
            reference_val = float(reference_nums[-1])

            # Allow 1% tolerance for floating point
            tolerance = abs(reference_val) * 0.01
            is_match = abs(student_val - reference_val) <= max(
                tolerance, 0.001
            )

            return {
                "numerical_match": is_match,
                "student_number": student_val,
                "reference_number": reference_val,
                "difference": abs(student_val - reference_val)
            }
        except (ValueError, IndexError):
            return {
                "numerical_match": False,
                "student_number": None,
                "reference_number": None
            }

    def check_formula_presence(
        self,
        student_answer: str,
        expected_formulas: list = None
    ) -> bool:
        """Check if mathematical formulas/equations are present."""
        # Look for equation patterns
        equation_patterns = [
            r'\d+\s*[+\-*/=]\s*\d+',  # Basic arithmetic
            r'[a-zA-Z]\s*=\s*[\d+\-*/a-zA-Z]',  # Variable assignment
            r'\d+\s*[²³⁴]',  # Exponents
            r'√\d+',  # Square root
            r'\d+/\d+',  # Fractions
        ]

        for pattern in equation_patterns:
            if re.search(pattern, student_answer):
                return True
        return False

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enhanced math evaluation with numerical checking."""

        # Get base LLM evaluation
        base_scores = await super().evaluate(
            question=question,
            reference_answer=reference_answer,
            student_answer=student_answer,
            grade_level=grade_level
        )

        # Check numerical answer
        num_check = self.check_numerical_answer(
            student_answer, reference_answer
        )

        # Boost correctness if numerical answer matches
        if num_check.get("numerical_match"):
            base_scores["correctness"] = max(
                base_scores["correctness"],
                0.85
            )
            logger.debug("Numerical answer matched - boosting score")

        # Check if formulas are shown
        has_formula = self.check_formula_presence(student_answer)
        if not has_formula and len(student_answer.split()) > 5:
            # Reduce clarity if no mathematical notation shown
            base_scores["clarity"] = base_scores["clarity"] * 0.9

        base_scores["numerical_check"] = num_check
        base_scores["has_formula"] = has_formula

        return base_scores


# Singleton
math_evaluator = MathEvaluator()
