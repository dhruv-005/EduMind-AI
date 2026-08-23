import re
import json
from typing import Dict, Any, List, Optional, Tuple
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    MATH_SYSTEM_PROMPT,
    MATH_EVALUATION_PROMPT,
)


class MathEvaluator:
    """Strict mathematics evaluator with numerical and method verification."""

    def _extract_all_numbers(self, text: str) -> List[float]:
        if not text:
            return []
        cleaned = text.replace('$', '').replace('\\', ' ')
        numbers = re.findall(r'-?\d+\.?\d*', cleaned)
        try:
            return [float(n) for n in numbers]
        except ValueError:
            return []

    def _extract_variable_values(self, text: str) -> Dict[str, float]:
        """Extract variable assignments like x=2, y=3 from text."""
        if not text:
            return {}
        cleaned = text.replace('$', '').replace('\\', ' ')
        # Match patterns like x = 2, y=3, x=2.5
        matches = re.findall(r'([a-zA-Z])\s*=\s*(-?\d+\.?\d*)', cleaned)
        result = {}
        for var, val in matches:
            var_lower = var.lower()
            if var_lower not in ('e', 'i'):  # skip constants
                try:
                    result[var_lower] = float(val)
                except ValueError:
                    pass
        return result

    def _extract_final_answer(self, text: str) -> Optional[float]:
        """Extract the final numerical answer."""
        if not text:
            return None
        cleaned = text.replace('$', '').replace('\\', ' ')

        explicit_patterns = [
            r'final\s*answer[:\s]*(-?\d+\.?\d*)',
            r'answer\s*(?:is|=)\s*(-?\d+\.?\d*)',
            r'result\s*(?:is|=)\s*(-?\d+\.?\d*)',
            r'leaves?\s+(?:her|him|them|it|me|us)\s+with\s+(-?\d+\.?\d*)',
            r'left\s+with\s+(-?\d+\.?\d*)',
            r'has\s+(-?\d+\.?\d*)\s+(?:apples?|left|remaining)',
            r'=\s*(-?\d+\.?\d*)\s*[\.\s]*$',
            r'(-?\d+\.?\d*)\s*$',
        ]

        for pattern in explicit_patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE | re.MULTILINE)
            if matches:
                try:
                    return float(matches[-1])
                except ValueError:
                    continue

        all_numbers = self._extract_all_numbers(text)
        return all_numbers[-1] if all_numbers else None

    def _check_bodmas_violation(self, student_answer: str) -> bool:
        text = student_answer.lower()
        violations = [
            r'first\s*,?\s*add.*then\s*divide',
            r'first\s*,?\s*add.*then\s*multiply',
            r'first\s*,?\s*subtract.*then\s*divide',
            r'processed?\s*left\s*to\s*right\s*without',
        ]
        for pattern in violations:
            if re.search(pattern, text):
                return True
        return False

    def _is_algebra_problem(self, question: str) -> bool:
        """Detect if this is an algebra/system of equations problem."""
        q_lower = question.lower()
        indicators = [
            'equation', 'solve for', 'system', 'linear',
            'substitute', 'eliminate', 'variable', 'unknown'
        ]
        return any(ind in q_lower for ind in indicators)

    def _check_final_answers_match(
        self, ref_text: str, stu_text: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Compare final answers — handles single values AND variable assignments."""
        ref_vars = self._extract_variable_values(ref_text)
        stu_vars = self._extract_variable_values(stu_text)

        # If both have variable assignments, compare each variable
        if ref_vars and stu_vars:
            correct_vars = {}
            wrong_vars = {}
            for var, ref_val in ref_vars.items():
                if var in stu_vars:
                    if abs(stu_vars[var] - ref_val) < 0.01:
                        correct_vars[var] = ref_val
                    else:
                        wrong_vars[var] = {
                            "student": stu_vars[var],
                            "correct": ref_val
                        }
                else:
                    wrong_vars[var] = {
                        "student": "missing",
                        "correct": ref_val
                    }

            all_correct = len(wrong_vars) == 0 and len(correct_vars) > 0
            return all_correct, {
                "correct_vars": correct_vars,
                "wrong_vars": wrong_vars,
                "type": "variables"
            }

        # Fallback: compare single final numbers
        ref_final = self._extract_final_answer(ref_text)
        stu_final = self._extract_final_answer(stu_text)

        if ref_final is not None and stu_final is not None:
            match = abs(ref_final - stu_final) < 0.01
            return match, {
                "ref_final": ref_final,
                "stu_final": stu_final,
                "type": "single_value"
            }

        return False, {"type": "unknown"}

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        """Evaluate math answer with strict numerical and method verification."""

        is_algebra = self._is_algebra_problem(question)
        final_match, answer_details = self._check_final_answers_match(
            reference_answer, student_answer
        )
        bodmas_violation = self._check_bodmas_violation(student_answer)

        logger.info(
            f"Math check: final_match={final_match}, "
            f"details={answer_details}, algebra={is_algebra}, "
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

        llm_method_correct = llm_data.get("method_correct", None)

        # ══════════════════════════════════════════════════════
        # STRICT OVERRIDE LOGIC
        # ══════════════════════════════════════════════════════

        if final_match and not bodmas_violation:
            # ── FINAL ANSWER CORRECT ──
            # But check if method is also correct (from LLM)
            if llm_method_correct is True or llm_method_correct is None:
                # Both answer and method correct → high score
                llm_data["correctness"] = max(llm_data.get("correctness", 0.5), 0.92)
                llm_data["completeness"] = max(llm_data.get("completeness", 0.5), 0.85)
                llm_data["relevance"] = max(llm_data.get("relevance", 0.5), 0.90)
                llm_data["clarity"] = max(llm_data.get("clarity", 0.5), 0.85)

                if not llm_data.get("feedback") or len(llm_data.get("feedback", "")) < 30:
                    llm_data["feedback"] = (
                        "Excellent work! Your final answer is correct and your method "
                        "is sound. You showed clear step-by-step reasoning. Great job!"
                    )
            else:
                # Answer correct but method flawed → moderate score
                llm_data["correctness"] = min(
                    max(llm_data.get("correctness", 0.5), 0.45), 0.55
                )
                llm_data["completeness"] = min(
                    llm_data.get("completeness", 1.0), 0.50
                )

                llm_data["feedback"] = (
                    f"Your final answer is numerically correct, but the method you used "
                    f"has issues. {llm_data.get('reasoning', '')} "
                    f"In mathematics, arriving at the right answer through an incorrect "
                    f"method can lead to wrong answers on harder problems. "
                    f"Please review the proper technique."
                )

            llm_data["final_answer_correct"] = True

        elif not final_match:
            # ── FINAL ANSWER WRONG ──
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.10)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.25)
            llm_data["final_answer_correct"] = False

            # Build specific feedback based on what went wrong
            if answer_details.get("type") == "variables":
                wrong = answer_details.get("wrong_vars", {})
                correct = answer_details.get("correct_vars", {})
                parts = []
                if correct:
                    correct_str = ", ".join(
                        f"{k}={v}" for k, v in correct.items()
                    )
                    parts.append(f"You correctly found {correct_str}.")
                if wrong:
                    for var, vals in wrong.items():
                        parts.append(
                            f"However, {var}={vals['student']} is wrong — "
                            f"the correct value is {var}={vals['correct']}."
                        )
                llm_data["feedback"] = " ".join(parts) + (
                    " Check your arithmetic carefully in the back-substitution step."
                )
            else:
                ref_val = answer_details.get("ref_final", "?")
                stu_val = answer_details.get("stu_final", "?")
                llm_data["feedback"] = (
                    f"Your final answer of {stu_val} is incorrect. "
                    f"The correct answer is {ref_val}. "
                    "Review each step of your calculation carefully."
                )

            # Context-aware suggestions (no BODMAS for algebra)
            if is_algebra:
                llm_data["improvement_suggestions"] = [
                    "Double-check your back-substitution arithmetic.",
                    "After solving, plug your values back into ALL original equations to verify.",
                    "Write each algebraic step on a separate line to avoid arithmetic slips.",
                ]
            elif bodmas_violation:
                llm_data["improvement_suggestions"] = [
                    "Follow BODMAS/PEMDAS: Brackets, Orders, Division, Multiplication, Addition, Subtraction.",
                    "Perform multiplication and division BEFORE addition and subtraction.",
                    "Write each step separately and verify the arithmetic.",
                ]
            else:
                llm_data["improvement_suggestions"] = [
                    "Re-check each arithmetic step carefully.",
                    "Verify your final answer by substituting back into the original problem.",
                    "Write each step on a separate line to catch errors early.",
                ]

        # Metadata
        llm_data["reference_final_answer"] = answer_details
        llm_data["student_final_answer"] = answer_details
        llm_data.setdefault("relevance", 0.7)
        llm_data.setdefault("clarity", 0.6)
        llm_data.setdefault("improvement_suggestions", [])
        llm_data.setdefault("feedback", "")
        llm_data.setdefault("reasoning", "")

        return llm_data


math_evaluator = MathEvaluator()
