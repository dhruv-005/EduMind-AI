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

    def _extract_final_answer(self, text: str) -> Optional[float]:
        """Extract the final numerical answer — prioritizes explicit final answers."""
        if not text:
            return None

        cleaned = text.replace('$', '').replace('\\', ' ')

        # Priority 1: Explicit final answer patterns (most reliable)
        explicit_patterns = [
            r'final\s*answer[:\s]*(-?\d+\.?\d*)',
            r'answer\s*(?:is|=)\s*(-?\d+\.?\d*)',
            r'result\s*(?:is|=)\s*(-?\d+\.?\d*)',
            r'leaves?\s+(?:her|him|them|it|me|us)\s+with\s+(-?\d+\.?\d*)',
            r'left\s+with\s+(-?\d+\.?\d*)',
            r'has\s+(-?\d+\.?\d*)\s+(?:apples?|left|remaining)',
            r'remaining\s+(?:is|=|:)\s*(-?\d+\.?\d*)',
            r'she\s+has\s+(-?\d+\.?\d*)\s+(?:apples?|left)',
            r'he\s+has\s+(-?\d+\.?\d*)\s+(?:apples?|left)',
            r'total\s+(?:is|=)\s*(-?\d+\.?\d*)',
        ]

        for pattern in explicit_patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            if matches:
                try:
                    val = float(matches[-1])
                    logger.debug(f"Math extractor: explicit match '{pattern}' = {val}")
                    return val
                except ValueError:
                    continue

        # Priority 2: Last number in the text (fallback)
        all_numbers = re.findall(r'-?\d+\.?\d*', cleaned)
        if all_numbers:
            try:
                val = float(all_numbers[-1])
                logger.debug(f"Math extractor: last number = {val}")
                return val
            except ValueError:
                pass

        return None

    def _check_bodmas_violation(self, student_answer: str) -> bool:
        """Detect order of operations violations."""
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
        """Check if student used correct operations."""
        stu_lower = student.lower()
        ref_lower = reference.lower()

        ref_ops = set()
        for op in re.findall(r'add|subtract|multiply|divide|\+|\-|\*|\/', ref_lower):
            if op in ('add', '+'): ref_ops.add('add')
            elif op in ('subtract', '-'): ref_ops.add('subtract')
            elif op in ('multiply', '*'): ref_ops.add('multiply')
            elif op in ('divide', '/'): ref_ops.add('divide')

        stu_ops = set()
        for op in re.findall(r'add|subtract|multiply|divide|added|subtracted|took|minus|plus|\+|\-|\*|\/', stu_lower):
            if op in ('add', 'plus', '+', 'added'): stu_ops.add('add')
            elif op in ('subtract', 'minus', '-', 'subtracted', 'took'): stu_ops.add('subtract')
            elif op in ('multiply', '*',): stu_ops.add('multiply')
            elif op in ('divide', '/'): stu_ops.add('divide')

        if ref_ops and stu_ops:
            overlap = ref_ops & stu_ops
            return len(overlap) >= len(ref_ops) * 0.5
        return True

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
            f"bodmas={bodmas_violation}"
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
                "reasoning": "LLM unavailable",
                "feedback": "", "improvement_suggestions": [],
            }

        # ══════════════════════════════════════════════════════
        # STRICT OVERRIDE
        # ══════════════════════════════════════════════════════

        if final_correct and method_correct and not bodmas_violation:
            # CORRECT ANSWER + CORRECT METHOD → HIGH SCORE
            llm_data["correctness"] = max(llm_data.get("correctness", 0.5), 0.92)
            llm_data["completeness"] = max(llm_data.get("completeness", 0.5), 0.85)
            llm_data["relevance"] = max(llm_data.get("relevance", 0.5), 0.90)
            llm_data["clarity"] = max(llm_data.get("clarity", 0.5), 0.85)
            llm_data["final_answer_correct"] = True
            llm_data["method_correct"] = True

            llm_data["reasoning"] = (
                f"Final answer ({stu_final}) matches reference ({ref_final}). "
                f"Method correct. No BODMAS violations."
            )

            if not llm_data.get("feedback") or len(llm_data.get("feedback", "")) < 30:
                llm_data["feedback"] = (
                    f"Excellent work! Your final answer of {int(stu_final) if stu_final == int(stu_final) else stu_final} "
                    f"is correct. You used the right method and showed clear steps. "
                    f"Keep up the great work!"
                )

            if not llm_data.get("improvement_suggestions"):
                llm_data["improvement_suggestions"] = [
                    "Your method is correct — keep using this step-by-step approach.",
                    "Try similar problems with larger numbers to build confidence.",
                    "Consider writing the equation form alongside your explanation.",
                ]

        elif final_correct and not method_correct:
            # CORRECT ANSWER + WRONG METHOD
            llm_data["correctness"] = min(max(llm_data.get("correctness", 0.5), 0.35), 0.45)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.50)
            llm_data["final_answer_correct"] = True
            llm_data["method_correct"] = False

            llm_data["feedback"] = (
                f"Your final answer of {stu_final} is correct, but your method has issues. "
                f"The correct approach is different from what you showed."
            )

        elif not final_correct and ref_final is not None:
            # WRONG ANSWER → HEAVY PENALTY
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.10)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.20)
            llm_data["final_answer_correct"] = False

            errors = []
            if bodmas_violation:
                errors.append("You did NOT follow BODMAS/PEMDAS order of operations.")
            errors.append(
                f"Your answer is {stu_final} but the correct answer is {ref_final}."
            )

            llm_data["feedback"] = (
                f"Your calculation is incorrect. " + " ".join(errors) + " "
                "Review each step carefully and verify your arithmetic."
            )

            llm_data["improvement_suggestions"] = [
                "Follow BODMAS/PEMDAS strictly.",
                f"Verify: your answer ({stu_final}) should satisfy the original problem.",
                "Write each step on a separate line.",
            ]

        # Metadata
        llm_data["reference_final_answer"] = ref_final
        llm_data["student_final_answer"] = stu_final
        llm_data.setdefault("relevance", 0.7)
        llm_data.setdefault("clarity", 0.6)
        llm_data.setdefault("improvement_suggestions", [])
        llm_data.setdefault("feedback", "")
        llm_data.setdefault("reasoning", "")

        return llm_data


math_evaluator = MathEvaluator()
