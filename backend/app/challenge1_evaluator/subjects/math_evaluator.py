import re
import json
from typing import Dict, Any, List, Optional, Tuple
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    EVALUATION_SYSTEM_PROMPT,
    MATH_SYSTEM_PROMPT
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
        """Extract standalone variable assignments like x = 2, y = 3 from text."""
        if not text:
            return {}
        cleaned = text.replace('$', '').replace('\\', ' ')
        matches = re.findall(r'\b([a-zA-Z])\s*=\s*(-?\d+\.?\d*)', cleaned)
        result = {}
        for var, val in matches:
            var_lower = var.lower()
            if var_lower not in ('e', 'i'):  # skip standard mathematical constants
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
        self, ref_text: str, stu_text: str, is_algebra: bool
    ) -> Tuple[bool, Dict[str, Any]]:
        """Compare final answers — handles single values AND variable assignments."""
        ref_vars = self._extract_variable_values(ref_text)
        stu_vars = self._extract_variable_values(stu_text)

        if is_algebra and ref_vars and stu_vars:
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

        is_algebra = self._is_algebra_problem(question)
        final_match, answer_details = self._check_final_answers_match(
            reference_answer, student_answer, is_algebra
        )
        bodmas_violation = self._check_bodmas_violation(student_answer)
        method_correct = self._check_method_correctness(reference_answer, student_answer)

        logger.info(
            f"Math check: final_match={final_match}, "
            f"details={answer_details}, algebra={is_algebra}, "
            f"bodmas={bodmas_violation}"
        )

        prompt = f"""You are a senior math examiner. Evaluate this student response strictly.

QUESTION:
{question}
GRADE LEVEL: {grade_level}

REFERENCE ANSWER:
{reference_answer}

STUDENT ANSWER:
{student_answer}

Return ONLY a valid JSON object matching this schema:
{{
  "correctness": <float 0.0 to 1.0>,
  "relevance": <float 0.0 to 1.0>,
  "completeness": <float 0.0 to 1.0>,
  "clarity": <float 0.0 to 1.0>,
  "correct_concepts": ["list of correct mathematical steps performed"],
  "missing_concepts": ["list of missing steps or principles"],
  "wrong_concepts": ["list of math errors, empty if none"],
  "reasoning": "Scoring explanation",
  "feedback": "Encouraging but mathematically precise feedback",
  "improvement_suggestions": ["1 to 3 suggestions"]
}}"""

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": f"{EVALUATION_SYSTEM_PROMPT}\n\n{MATH_SYSTEM_PROMPT}"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            raw = result["text"]
            start = raw.find('{')
            end = raw.rfind('}') + 1
            if start != -1 and end > start:
                llm_data = json.loads(raw[start:end])
            else:
                raise ValueError("No JSON")
        except Exception as e:
            logger.error(f"Math LLM failed: {e}")
            llm_data = {
                "correctness": 0.5, "relevance": 0.7, "completeness": 0.5, "clarity": 0.6,
                "correct_concepts": [], "missing_concepts": [], "wrong_concepts": [],
                "reasoning": "LLM failed", "feedback": "", "improvement_suggestions": [],
            }

        # ── STRICT OVERRIDE ────────────────────────────────────
        if final_match and not bodmas_violation:
            if method_correct:
                llm_data["correctness"] = max(llm_data.get("correctness", 0.5), 0.95)
                llm_data["completeness"] = max(llm_data.get("completeness", 0.5), 0.90)
                llm_data["final_answer_correct"] = True
                llm_data["method_correct"] = True
            else:
                llm_data["correctness"] = min(max(llm_data.get("correctness", 0.5), 0.45), 0.55)
                llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.50)
                llm_data["final_answer_correct"] = True
                llm_data["method_correct"] = False
        else:
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.15)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.25)
            llm_data["final_answer_correct"] = False
            llm_data["method_correct"] = False

        llm_data.setdefault("correct_concepts", [])
        llm_data.setdefault("missing_concepts", [])
        llm_data.setdefault("wrong_concepts", [])
        return llm_data

# Singleton
math_evaluator = MathEvaluator()
