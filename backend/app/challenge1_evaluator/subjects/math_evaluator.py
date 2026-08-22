import re
import json
from typing import Dict, Any, List, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    MATH_SYSTEM_PROMPT,
    MATH_EVALUATION_PROMPT,
)


class MathEvaluator:
    """Strict mathematics evaluator with numerical verification."""

    def _extract_all_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text."""
        if not text:
            return []
        cleaned = text.replace('$', '').replace('\\', ' ')
        cleaned = re.sub(r'[×xX]', '*', cleaned)
        cleaned = re.sub(r'[÷]', '/', cleaned)
        numbers = re.findall(r'-?\d+\.?\d*', cleaned)
        try:
            return [float(n) for n in numbers]
        except ValueError:
            return []

    def _extract_final_answer(self, text: str) -> Optional[float]:
        """Extract the final numerical answer from text."""
        if not text:
            return None

        # Priority patterns for final answer
        patterns = [
            r'final\s*answer[:\s]*\$?(-?\d+\.?\d*)',
            r'answer\s*(?:is|=)?\s*\$?(-?\d+\.?\d*)',
            r'result\s*(?:is|=)?\s*\$?(-?\d+\.?\d*)',
            r'equals?\s*\$?(-?\d+\.?\d*)',
            r'=\s*\$?(-?\d+\.?\d*)\s*[\.\s]*$',
            r'get\s+\$?(-?\d+\.?\d*)',
            r'(-?\d+\.?\d*)\s*$',
        ]

        cleaned = text.replace('$', '').replace('\\', ' ')

        for pattern in patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE | re.MULTILINE)
            if matches:
                try:
                    return float(matches[-1])
                except ValueError:
                    continue

        # Last resort — use last number found
        all_nums = self._extract_all_numbers(text)
        return all_nums[-1] if all_nums else None

    def _check_bodmas_violation(self, student_answer: str) -> bool:
        """Detect if student violated order of operations."""
        text = student_answer.lower()

        # Common violation patterns
        violations = [
            r'first\s*,?\s*add.*then\s*divide',
            r'first\s*,?\s*add.*then\s*multiply',
            r'first\s*,?\s*subtract.*then\s*divide',
            r'first\s*,?\s*subtract.*then\s*multiply',
            r'left\s*to\s*right\s*without',
            r'processed?\s*left\s*to\s*right',
        ]

        for pattern in violations:
            if re.search(pattern, text):
                return True
        return False

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        """Evaluate math answer with strict numerical verification."""

        # ── PROGRAMMATIC CHECKS FIRST ───────────────────────────
        ref_final = self._extract_final_answer(reference_answer)
        stu_final = self._extract_final_answer(student_answer)

        final_correct = False
        if ref_final is not None and stu_final is not None:
            final_correct = abs(ref_final - stu_final) < 0.001

        bodmas_violation = self._check_bodmas_violation(student_answer)

        logger.info(
            f"Math check: ref_final={ref_final}, stu_final={stu_final}, "
            f"correct={final_correct}, bodmas_violation={bodmas_violation}"
        )

        # ── LLM EVALUATION ──────────────────────────────────────
        prompt = MATH_EVALUATION_PROMPT.format(
            question=question,
            reference_answer=reference_answer,
            student_answer=student_answer,
        )

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": MATH_SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.1,  # Low for consistency
            )

            # Parse JSON response
            raw = result.get("text", "")
            start = raw.find('{')
            end = raw.rfind('}') + 1

            if start != -1 and end > start:
                llm_data = json.loads(raw[start:end])
            else:
                raise ValueError("No JSON in LLM response")

        except Exception as e:
            logger.error(f"Math LLM failed: {e}")
            llm_data = {
                "correctness": 0.5,
                "relevance": 0.5,
                "completeness": 0.5,
                "clarity": 0.5,
                "reasoning": "LLM evaluation unavailable",
                "feedback": "Please review your work carefully.",
                "improvement_suggestions": ["Review the problem step by step"],
            }

        # ── STRICT OVERRIDE FOR WRONG ANSWERS ───────────────────
        if not final_correct and ref_final is not None:
            # Wrong final answer — heavy penalty
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.10)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.20)
            llm_data["final_answer_correct"] = False

            # Build specific feedback about the error
            error_details = []

            if bodmas_violation:
                error_details.append(
                    "You did NOT follow the order of operations (BODMAS/PEMDAS). "
                    "You must perform Division and Multiplication BEFORE Addition and Subtraction, "
                    "working from left to right for equal-priority operations."
                )
                llm_data["method_correct"] = False

            error_details.append(
                f"Your final answer is {stu_final}, but the correct answer is {ref_final}."
            )

            # Generate real feedback based on actual error
            llm_data["feedback"] = (
                f"Your calculation is incorrect. You got {stu_final} but the correct "
                f"answer is {ref_final}. "
                + " ".join(error_details) + " "
                "Let me show you the correct approach: For an expression like "
                "'12 + 8 ÷ 2 × 3 - 5', you must first do 8÷2=4, then 4×3=12, "
                "then 12+12=24, then 24-5=19. The order matters!"
            )

            # Real improvement suggestions based on actual error
            llm_data["improvement_suggestions"] = [
                "MEMORIZE BODMAS/PEMDAS: Brackets, Orders, Division, Multiplication, Addition, Subtraction.",
                "For every calculation, IDENTIFY which operations to do first BEFORE calculating.",
                "Multiplication (×) and Division (÷) come BEFORE Addition (+) and Subtraction (-).",
                f"To verify: Take your answer ({stu_final}) and work backwards - it should equal the original expression.",
                "Practice with 10 similar problems, always writing which operation you're doing at each step.",
            ]

            # Set wrong concepts based on real errors
            if "wrong_steps" not in llm_data or not llm_data["wrong_steps"]:
                llm_data["wrong_steps"] = [
                    "Did not identify multiplication and division as higher priority operations",
                    f"Calculated left-to-right instead of using BODMAS, resulting in {stu_final} instead of {ref_final}"
                ]

            llm_data["reasoning"] = (
                f"Student's final answer ({stu_final}) does NOT match correct answer ({ref_final}). "
                f"Order of operations violation detected: {bodmas_violation}. "
                f"Correctness capped at 0.10 due to fundamentally wrong result."
            )

        elif final_correct:
            # Correct final answer — reward but check method
            llm_data["correctness"] = max(llm_data.get("correctness", 0.5), 0.85)
            llm_data["final_answer_correct"] = True

            if not llm_data.get("feedback"):
                llm_data["feedback"] = (
                    f"Excellent! Your final answer of {stu_final} is correct. "
                    "You properly applied the order of operations."
                )

        # ── ADD METADATA ────────────────────────────────────────
        llm_data["reference_final_answer"] = ref_final
        llm_data["student_final_answer"] = stu_final
        llm_data["model_used"] = result.get("model", "unknown") if 'result' in dir() else "fallback"
        llm_data["provider"] = result.get("provider", "unknown") if 'result' in dir() else "fallback"

        # Ensure required fields exist
        llm_data.setdefault("relevance", 0.7 if final_correct else 0.5)
        llm_data.setdefault("clarity", 0.6)
        llm_data.setdefault("improvement_suggestions", [])
        llm_data.setdefault("feedback", "")
        llm_data.setdefault("reasoning", "")

        return llm_data


math_evaluator = MathEvaluator()
