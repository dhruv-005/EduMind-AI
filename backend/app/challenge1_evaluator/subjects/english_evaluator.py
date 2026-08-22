import json
import re
from typing import Dict, Any, List
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    ENGLISH_SYSTEM_PROMPT,
    ENGLISH_EVALUATION_PROMPT,
)


class EnglishEvaluator:
    """Strict English evaluator with language assessment."""

    def _basic_grammar_check(self, text: str) -> List[str]:
        """Basic grammar checks."""
        errors = []

        # Sentence structure
        sentences = re.split(r'[.!?]+', text)
        for s in sentences:
            s = s.strip()
            if len(s) > 100:
                errors.append("Very long sentence — consider breaking into shorter ones")
            if s and not s[0].isupper():
                errors.append("Sentence should start with capital letter")

        # Double spaces
        if '  ' in text:
            errors.append("Multiple spaces between words")

        # Missing capitalization for 'I'
        if re.search(r'\bi\b', text):
            errors.append("The pronoun 'I' should always be capitalized")

        return errors[:5]  # Limit errors

    def _word_count(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        """Evaluate English answer with language assessment."""

        # Basic checks
        grammar_errors = self._basic_grammar_check(student_answer)
        ref_word_count = self._word_count(reference_answer)
        stu_word_count = self._word_count(student_answer)
        length_ratio = stu_word_count / max(ref_word_count, 1)

        logger.info(
            f"English check: grammar_errors={len(grammar_errors)}, "
            f"length_ratio={length_ratio:.2f} ({stu_word_count}/{ref_word_count})"
        )

        prompt = ENGLISH_EVALUATION_PROMPT.format(
            question=question,
            reference_answer=reference_answer,
            student_answer=student_answer,
        )

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": ENGLISH_SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.2,
            )

            raw = result.get("text", "")
            start = raw.find('{')
            end = raw.rfind('}') + 1

            if start != -1 and end > start:
                llm_data = json.loads(raw[start:end])
            else:
                raise ValueError("No JSON response")

        except Exception as e:
            logger.error(f"English LLM failed: {e}")
            llm_data = {
                "correctness": 0.6,
                "relevance": 0.6,
                "completeness": min(1.0, length_ratio),
                "clarity": 0.6,
                "grammar_errors": grammar_errors,
                "wrong_interpretations": [],
                "correct_points": [],
                "missing_analysis": [],
                "reasoning": "Automated assessment",
                "feedback": "Review your grammar and expand your analysis.",
                "improvement_suggestions": ["Improve grammar", "Add more detail"],
            }

        # ── STRICTNESS ADJUSTMENTS ──────────────────────────────
        # Too short answer
        if length_ratio < 0.3:
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.35)

        # Many grammar errors
        if len(grammar_errors) >= 3:
            llm_data["clarity"] = min(llm_data.get("clarity", 1.0), 0.50)

        # Wrong interpretations detected
        wrong_interp = llm_data.get("wrong_interpretations", [])
        if wrong_interp:
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.40)

        # Build real feedback
        if not llm_data.get("feedback") or "review" in llm_data.get("feedback", "").lower()[:20]:
            feedback_parts = []

            if wrong_interp:
                feedback_parts.append(
                    f"You made some interpretation errors: {'; '.join(wrong_interp[:2])}."
                )

            if grammar_errors:
                feedback_parts.append(
                    f"Grammar issues found: {'; '.join(grammar_errors[:2])}."
                )

            correct_points = llm_data.get("correct_points", [])
            if correct_points:
                feedback_parts.append(
                    f"Good aspects: {'; '.join(correct_points[:2])}."
                )

            missing = llm_data.get("missing_analysis", [])
            if missing:
                feedback_parts.append(
                    f"You should have discussed: {'; '.join(missing[:2])}."
                )

            if length_ratio < 0.5:
                feedback_parts.append(
                    f"Your answer is too brief ({stu_word_count} words vs reference {ref_word_count} words). Develop your ideas more fully."
                )

            llm_data["feedback"] = " ".join(feedback_parts) if feedback_parts else (
                "Your answer demonstrates understanding of the topic. Continue to develop analytical depth."
            )

        # Real improvement suggestions
        if not llm_data.get("improvement_suggestions") or len(llm_data.get("improvement_suggestions", [])) < 2:
            suggestions = []

            if grammar_errors:
                suggestions.append(
                    f"Fix these grammar issues: {'; '.join(grammar_errors[:2])}."
                )

            if wrong_interp:
                suggestions.append(
                    "Re-read the text carefully — some of your interpretations don't match the source."
                )

            if length_ratio < 0.5:
                suggestions.append(
                    f"Expand your answer with more evidence and analysis (aim for {ref_word_count} words minimum)."
                )

            if missing:
                suggestions.append(
                    f"Address these aspects you missed: {'; '.join(missing[:2])}."
                )

            suggestions.append(
                "Structure your answer: Thesis → Evidence → Analysis → Conclusion."
            )

            llm_data["improvement_suggestions"] = suggestions[:5]

        # Metadata
        llm_data["word_count"] = stu_word_count
        llm_data["reference_word_count"] = ref_word_count
        llm_data["basic_grammar_check"] = grammar_errors
        llm_data["model_used"] = result.get("model", "fallback") if 'result' in dir() else "fallback"
        llm_data["provider"] = result.get("provider", "fallback") if 'result' in dir() else "fallback"

        # Ensure required fields
        llm_data.setdefault("relevance", 0.7)
        llm_data.setdefault("reasoning", "English language assessment complete")

        return llm_data


english_evaluator = EnglishEvaluator()
