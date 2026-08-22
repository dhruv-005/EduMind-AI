import json
import re
from typing import Dict, Any, List, Set
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    GENERAL_SYSTEM_PROMPT,
    GENERAL_EVALUATION_PROMPT,
)


class GeneralEvaluator:
    """Strict general evaluator for any subject."""

    def _extract_key_phrases(self, text: str) -> Set[str]:
        """Extract key phrases (nouns, dates, numbers)."""
        if not text:
            return set()

        # Numbers and dates
        numbers = re.findall(r'\b\d{2,4}\b', text)

        # Capitalized words (likely important names/concepts)
        proper_nouns = re.findall(r'\b[A-Z][a-z]{2,}\b', text)

        # Multi-word capitalized phrases
        multi_caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)

        return set(numbers + proper_nouns + multi_caps)

    def _calculate_fact_overlap(
        self, reference: str, student: str
    ) -> Dict[str, Any]:
        """Calculate how many key facts from reference appear in student answer."""
        ref_phrases = self._extract_key_phrases(reference)
        stu_phrases = self._extract_key_phrases(student)

        matched = ref_phrases & stu_phrases
        missing = ref_phrases - stu_phrases
        extra = stu_phrases - ref_phrases

        coverage = len(matched) / max(len(ref_phrases), 1)

        return {
            "reference_facts": list(ref_phrases),
            "student_facts": list(stu_phrases),
            "matched_facts": list(matched),
            "missing_facts": list(missing),
            "extra_facts": list(extra),
            "coverage": coverage,
        }

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        """Evaluate general answer with fact verification."""

        # Programmatic fact analysis
        fact_analysis = self._calculate_fact_overlap(reference_answer, student_answer)

        logger.info(
            f"General check: coverage={fact_analysis['coverage']:.2f}, "
            f"matched={len(fact_analysis['matched_facts'])}, "
            f"missing={len(fact_analysis['missing_facts'])}"
        )

        prompt = GENERAL_EVALUATION_PROMPT.format(
            question=question,
            subject="general",
            reference_answer=reference_answer,
            student_answer=student_answer,
        )

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": GENERAL_SYSTEM_PROMPT},
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
                raise ValueError("No JSON in response")

        except Exception as e:
            logger.error(f"General LLM failed: {e}")
            llm_data = self._fallback_result(fact_analysis)

        # ── STRICTNESS CHECKS ──────────────────────────────────
        coverage = fact_analysis["coverage"]

        # Low fact coverage
        if coverage < 0.3:
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.30)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.25)

        # Wrong facts detected
        wrong_facts = llm_data.get("facts_wrong", [])
        if wrong_facts and len(wrong_facts) > 0:
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.35)

        # ── BUILD REAL FEEDBACK ─────────────────────────────────
        if not llm_data.get("feedback") or len(llm_data.get("feedback", "")) < 50:
            feedback_parts = []

            correct = llm_data.get("facts_correct", [])
            if correct:
                feedback_parts.append(
                    f"You correctly mentioned: {', '.join(correct[:3])}."
                )

            wrong = llm_data.get("facts_wrong", [])
            if wrong:
                feedback_parts.append(
                    f"However, these claims are incorrect: {'; '.join(wrong[:2])}."
                )

            missing = llm_data.get("facts_missing", [])
            if missing:
                feedback_parts.append(
                    f"You missed important facts: {', '.join(missing[:4])}."
                )
            elif fact_analysis["missing_facts"]:
                feedback_parts.append(
                    f"You should have mentioned: {', '.join(fact_analysis['missing_facts'][:4])}."
                )

            if coverage < 0.5:
                feedback_parts.append(
                    f"Your answer only covers {coverage:.0%} of the key points from the reference answer."
                )

            llm_data["feedback"] = " ".join(feedback_parts) if feedback_parts else (
                "Your answer needs more depth and specific details. Focus on the key concepts and facts."
            )

        # Real suggestions
        if not llm_data.get("improvement_suggestions") or len(llm_data.get("improvement_suggestions", [])) < 2:
            suggestions = []

            missing = llm_data.get("facts_missing", []) or fact_analysis["missing_facts"]
            if missing:
                suggestions.append(
                    f"Include these key points in your answer: {', '.join(missing[:4])}."
                )

            wrong = llm_data.get("facts_wrong", [])
            if wrong:
                suggestions.append(
                    "Review the material — some facts in your answer are incorrect."
                )

            if coverage < 0.5:
                suggestions.append(
                    f"Study the reference material more thoroughly — your answer only addresses {coverage:.0%} of expected content."
                )

            suggestions.append(
                "Structure your answer with: Main point → Supporting details → Examples → Conclusion."
            )

            suggestions.append(
                "Before writing, list the key facts you need to include to ensure completeness."
            )

            llm_data["improvement_suggestions"] = suggestions[:5]

        # Metadata
        llm_data["fact_coverage"] = round(coverage, 2)
        llm_data["matched_facts"] = fact_analysis["matched_facts"]
        llm_data["missing_facts"] = llm_data.get("facts_missing") or fact_analysis["missing_facts"]
        llm_data["model_used"] = result.get("model", "fallback") if 'result' in dir() else "fallback"
        llm_data["provider"] = result.get("provider", "fallback") if 'result' in dir() else "fallback"

        # Ensure required fields
        llm_data.setdefault("relevance", 0.7)
        llm_data.setdefault("clarity", 0.6)
        llm_data.setdefault("reasoning", f"General evaluation: {coverage:.0%} fact coverage")

        return llm_data

    def _fallback_result(self, fact_analysis: dict) -> dict:
        """Fallback result if LLM fails."""
        coverage = fact_analysis["coverage"]
        return {
            "correctness": max(0.2, coverage * 0.8),
            "relevance": 0.6,
            "completeness": coverage,
            "clarity": 0.6,
            "key_facts_reference": fact_analysis["reference_facts"],
            "facts_correct": fact_analysis["matched_facts"],
            "facts_wrong": [],
            "facts_missing": fact_analysis["missing_facts"],
            "reasoning": f"Rule-based: {coverage:.0%} fact coverage",
            "feedback": (
                f"Your answer covers {coverage:.0%} of the key facts. "
                f"Missing: {', '.join(fact_analysis['missing_facts'][:3])}"
            ),
            "improvement_suggestions": [
                f"Include: {', '.join(fact_analysis['missing_facts'][:3])}",
                "Verify all facts before including them",
                "Provide specific examples and details",
            ],
        }


general_evaluator = GeneralEvaluator()
