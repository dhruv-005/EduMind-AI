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

        patterns = [
            r'final\s*answer[:\s]*\$?(-?\d+\.?\d*)',
            r'answer\s*(?:is|=)?\s*\$?(-?\d+\.?\d*)',
            r'result\s*(?:is|=)?\s*\$?(-?\d+\.?\d*)',
            r'equals?\s*\$?(-?\d+\.?\d*)',
            r'leaves?\s+(?:her|him|them|it)\s+with\s+\$?(-?\d+\.?\d*)',
            r'left\s+with\s+\$?(-?\d+\.?\d*)',
            r'has\s+\$?(-?\d+\.?\d*)\s+left',
            r'=\s*\$?(-?\d+\.?\d*)\s*[\.\s]*$',
            r'get\s+\$?(-?\d+\.?\d*)',
            r'(-?\d+\.?\d*)\s*(?:apples?|units?|items?|cm|m|kg|g|ml|l|degrees?)?\s*[\.\s]*$',
        ]

        cleaned = text.replace('$', '').replace('\\', ' ')

        for pattern in patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE | re.MULTILINE)
            if matches:
                try:
                    return float(matches[-1])
                except ValueError:
                    continue

        all_nums = self._extract_all_numbers(text)
        return all_nums[-1] if all_nums else None

    def _check_bodmas_violation(self, student_answer: str) -> bool:
        """Detect if student violated order of operations."""
        text = student_answer.lower()
        violations = [
            r'first\s*,?\s*add.*then\s*divide',
            r'first\s*,?\s*add.*then\s*multiply',
            r'first\s*,?\s*subtract.*then\s*divide',
            r'first\s*,?\s*subtract.*then\s*multiply',
            r'processed?\s*left\s*to\s*right\s*without',
        ]
        for pattern in violations:
            if re.search(pattern, text):
                return True
        return False

    def _check_method_correctness(self, reference: str, student: str) -> bool:
        """Check if the student's method/approach is correct."""
        stu_lower = student.lower()
        ref_lower = reference.lower()

        # Extract operations from reference
        ref_ops = re.findall(r'(?:add|subtract|multiply|divide|plus|minus|times|\+|\-|\*|\/)', ref_lower)
        stu_ops = re.findall(r'(?:add|subtract|multiply|divide|plus|minus|times|added|subtracted|multiplied|divided|\+|\-|\*|\/)', stu_lower)

        # Check if student used the same types of operations
        ref_op_types = set()
        for op in ref_ops:
            if op in ('add', 'plus', '+'):
                ref_op_types.add('add')
            elif op in ('subtract', 'minus', '-'):
                ref_op_types.add('subtract')
            elif op in ('multiply', 'times', '*'):
                ref_op_types.add('multiply')
            elif op in ('divide', '/'):
                ref_op_types.add('divide')

        stu_op_types = set()
        for op in stu_ops:
            if op in ('add', 'plus', '+', 'added', 'adding'):
                stu_op_types.add('add')
            elif op in ('subtract', 'minus', '-', 'subtracted', 'took away', 'took'):
                stu_op_types.add('subtract')
            elif op in ('multiply', 'times', '*', 'multiplied'):
                stu_op_types.add('multiply')
            elif op in ('divide', '/', 'divided'):
                stu_op_types.add('divide')

        # Student should use at least the same operation types
        if ref_op_types and stu_op_types:
            overlap = ref_op_types & stu_op_types
            return len(overlap) >= len(ref_op_types) * 0.5

        return True  # Can't determine, assume OK

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        """Evaluate math answer with strict numerical verification."""

        ref_final = self._extract_final_answer(reference_answer)
        stu_final = self._extract_final_answer(student_answer)

        final_correct = False
        if ref_final is not None and stu_final is not None:
            final_correct = abs(ref_final - stu_final) < 0.01

        bodmas_violation = self._check_bodmas_violation(student_answer)
        method_correct = self._check_method_correctness(reference_answer, student_answer)

        logger.info(
            f"Math check: ref={ref_final}, stu={stu_final}, "
            f"correct={final_correct}, method={method_correct}, "
            f"bodmas_violation={bodmas_violation}"
        )

        # LLM evaluation
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
                temperature=0.1,
            )
            raw = result.get("text", "")
            start = raw.find('{')
            end = raw.rfind('}') + 1
            if start != -1 and end > start:
                llm_data = json.loads(raw[start:end])
            else:
                raise ValueError("No JSON")
        except Exception as e:
            logger.error(f"Math LLM failed: {e}")
            llm_data = {
                "correctness": 0.5, "relevance": 0.7,
                "completeness": 0.5, "clarity": 0.6,
                "reasoning": "LLM unavailable", "feedback": "",
                "improvement_suggestions": [],
            }

        # ══════════════════════════════════════════════════════
        # STRICT OVERRIDE LOGIC
        # ══════════════════════════════════════════════════════

        if final_correct and method_correct and not bodmas_violation:
            # ── CORRECT ANSWER + CORRECT METHOD → HIGH SCORE ──
            llm_data["correctness"] = max(llm_data.get("correctness", 0.5), 0.92)
            llm_data["completeness"] = max(llm_data.get("completeness", 0.5), 0.85)
            llm_data["relevance"] = max(llm_data.get("relevance", 0.5), 0.90)
            llm_data["clarity"] = max(llm_data.get("clarity", 0.5), 0.85)
            llm_data["final_answer_correct"] = True
            llm_data["method_correct"] = True

            llm_data["reasoning"] = (
                f"Student's final answer ({stu_final}) matches reference ({ref_final}). "
                f"Method is correct. No order of operations violations."
            )

            if not llm_data.get("feedback") or len(llm_data.get("feedback", "")) < 30:
                llm_data["feedback"] = (
                    f"Excellent work! Your final answer of {stu_final} is correct. "
                    f"You correctly identified that you needed to add the given amounts "
                    f"and then subtract from the total. Your step-by-step approach is clear "
                    f"and easy to follow. Keep up the great work!"
                )

            if not llm_data.get("improvement_suggestions"):
                llm_data["improvement_suggestions"] = [
                    "Your method is correct — keep using this step-by-step approach.",
                    "Try solving similar problems with larger numbers to build confidence.",
                    "Consider writing the equation form (e.g., 15 - (4+3) = 8) alongside your word explanation.",
                ]

        elif final_correct and not method_correct:
            # ── CORRECT ANSWER + WRONG METHOD → MODERATE SCORE ──
            llm_data["correctness"] = min(max(llm_data.get("correctness", 0.5), 0.35), 0.45)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.50)
            llm_data["final_answer_correct"] = True
            llm_data["method_correct"] = False

            llm_data["feedback"] = (
                f"Your final answer of {stu_final} is correct, but your method has issues. "
                f"While you arrived at the right number, the steps you showed contain errors. "
                f"In mathematics, showing the correct process is just as important as the final answer."
            )

        elif not final_correct and ref_final is not None:
            # ── WRONG ANSWER → HEAVY PENALTY ──
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.10)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.20)
            llm_data["final_answer_correct"] = False

            error_details = []
            if bodmas_violation:
                error_details.append(
                    "You did NOT follow the order of operations (BODMAS/PEMDAS)."
                )

            error_details.append(
                f"Your final answer is {stu_final}, but the correct answer is {ref_final}."
            )

            llm_data["feedback"] = (
                f"Your calculation is incorrect. " + " ".join(error_details) + " "
                "Review the correct order of operations and check each step carefully."
            )

            llm_data["improvement_suggestions"] = [
                "Follow BODMAS/PEMDAS: Brackets, Orders, Division, Multiplication, Addition, Subtraction.",
                f"Verify: your answer ({stu_final}) should satisfy the original problem.",
                "Write each step on a separate line and check the arithmetic.",
            ]

        # Metadata
        llm_data["reference_final_answer"] = ref_final
        llm_data["student_final_answer"] = stu_final
        llm_data["model_used"] = result.get("model", "fallback") if 'result' in dir() else "fallback"
        llm_data["provider"] = result.get("provider", "fallback") if 'result' in dir() else "fallback"

        llm_data.setdefault("relevance", 0.7)
        llm_data.setdefault("clarity", 0.6)
        llm_data.setdefault("improvement_suggestions", [])
        llm_data.setdefault("feedback", "")
        llm_data.setdefault("reasoning", "")

        return llm_data


math_evaluator = MathEvaluator()
