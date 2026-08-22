import json
import re
from typing import Dict, Any, List
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    SCIENCE_SYSTEM_PROMPT,
    SCIENCE_EVALUATION_PROMPT,
)


class ScienceEvaluator:
    """Strict science evaluator with fact verification."""

    def _extract_scientific_terms(self, text: str) -> List[str]:
        """Extract scientific terminology from text."""
        # Common scientific term patterns
        terms = re.findall(
            r'\b(?:photosynthesis|chlorophyll|glucose|oxygen|carbon\s*dioxide|'
            r'mitochondria|nucleus|cell|DNA|RNA|protein|enzyme|molecule|'
            r'atom|electron|proton|neutron|force|gravity|velocity|acceleration|'
            r'energy|mass|momentum|newton|law|theory|hypothesis)\b',
            text.lower()
        )
        return list(set(terms))

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        """Evaluate science answer with fact verification."""

        # Extract scientific terms from both answers
        ref_terms = self._extract_scientific_terms(reference_answer)
        stu_terms = self._extract_scientific_terms(student_answer)

        # Check terminology coverage
        common_terms = set(ref_terms) & set(stu_terms)
        missing_terms = set(ref_terms) - set(stu_terms)

        term_coverage = len(common_terms) / max(len(ref_terms), 1)

        logger.info(
            f"Science check: ref_terms={len(ref_terms)}, stu_terms={len(stu_terms)}, "
            f"common={len(common_terms)}, coverage={term_coverage:.2f}"
        )

        # LLM evaluation
        prompt = SCIENCE_EVALUATION_PROMPT.format(
            question=question,
            reference_answer=reference_answer,
            student_answer=student_answer,
        )

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": SCIENCE_SYSTEM_PROMPT},
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
            logger.error(f"Science LLM failed: {e}")
            llm_data = self._fallback_result(
                ref_terms, stu_terms, common_terms, missing_terms, term_coverage
            )

        # ── STRICTNESS CHECKS ──────────────────────────────────
        # If very few key terms are present, penalize
        if term_coverage < 0.3:
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.30)
            llm_data["completeness"] = min(llm_data.get("completeness", 1.0), 0.25)

        # If wrong scientific facts detected
        wrong_facts = llm_data.get("wrong_scientific_facts", [])
        if wrong_facts and len(wrong_facts) > 0:
            llm_data["correctness"] = min(llm_data.get("correctness", 1.0), 0.35)

            # Build real feedback
            errors_str = "; ".join(wrong_facts[:3])
            llm_data["feedback"] = (
                f"Your answer contains scientific inaccuracies: {errors_str}. "
                f"You correctly mentioned: {', '.join(list(common_terms)[:5]) if common_terms else 'few relevant terms'}. "
                f"However, you missed key concepts: {', '.join(list(missing_terms)[:5]) if missing_terms else 'the main scientific principles'}. "
                "In science, precision matters — using correct terminology and stating accurate facts is essential."
            )

        # Real suggestions based on actual gaps
        if not llm_data.get("improvement_suggestions"):
            suggestions = []
            if missing_terms:
                suggestions.append(
                    f"Include these key scientific terms in your answer: {', '.join(list(missing_terms)[:5])}."
                )
            if wrong_facts:
                suggestions.append(
                    "Review your textbook chapter on this topic — some facts you stated are incorrect."
                )
            if term_coverage < 0.5:
                suggestions.append(
                    "Study the scientific vocabulary related to this topic — use precise terminology."
                )
            suggestions.append(
                "For science answers: state the principle, explain the mechanism, and give a specific example."
            )
            llm_data["improvement_suggestions"] = suggestions

        # Ensure feedback exists
        if not llm_data.get("feedback"):
            if term_coverage >= 0.7 and not wrong_facts:
                llm_data["feedback"] = (
                    f"Good work! You covered the main concepts including: {', '.join(list(common_terms)[:4])}. "
                    "Your scientific understanding is solid."
                )
            else:
                missing_str = ', '.join(list(missing_terms)[:4]) if missing_terms else "some key concepts"
                llm_data["feedback"] = (
                    f"You covered {len(common_terms)} out of {len(ref_terms)} key scientific concepts. "
                    f"You need to include: {missing_str}. "
                    "Focus on using precise scientific terminology and explaining the mechanisms clearly."
                )

        # Metadata
        llm_data["scientific_terms_covered"] = list(common_terms)
        llm_data["scientific_terms_missing"] = list(missing_terms)
        llm_data["terminology_coverage"] = round(term_coverage, 2)
        llm_data["model_used"] = result.get("model", "fallback") if 'result' in dir() else "fallback"
        llm_data["provider"] = result.get("provider", "fallback") if 'result' in dir() else "fallback"

        # Ensure required fields
        llm_data.setdefault("relevance", 0.7)
        llm_data.setdefault("clarity", 0.6)
        llm_data.setdefault("reasoning", f"Science evaluation: {term_coverage:.0%} terminology coverage")

        return llm_data

    def _fallback_result(self, ref_terms, stu_terms, common, missing, coverage):
        """Fallback if LLM fails."""
        return {
            "correctness": max(0.2, coverage * 0.8),
            "relevance": 0.6,
            "completeness": coverage,
            "clarity": 0.6,
            "correct_scientific_facts": list(common),
            "wrong_scientific_facts": [],
            "missing_key_concepts": list(missing),
            "terminology_errors": [],
            "reasoning": f"Rule-based evaluation: {coverage:.0%} term coverage",
            "feedback": f"You covered {len(common)}/{len(ref_terms)} key scientific concepts. Missing: {', '.join(list(missing)[:3])}",
            "improvement_suggestions": [
                f"Include these concepts: {', '.join(list(missing)[:3])}",
                "Use precise scientific terminology",
                "Explain the mechanism, not just the outcome",
            ],
        }


science_evaluator = ScienceEvaluator()
