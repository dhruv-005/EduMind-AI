import json
import re
from typing import Dict, Any, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client


class BaseEvaluator:
    """
    Base class for all subject-specific evaluators.
    """

    subject_name = "general"

    def build_evaluation_prompt(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: Optional[str] = None
    ) -> str:
        level = f"Grade Level: {grade_level}" if grade_level else ""
        return f"""You are an expert {self.subject_name} teacher evaluating a student's answer.

{level}
Question: {question}
Reference Answer: {reference_answer[:600]}
Student Answer: {student_answer[:600]}

Evaluate and provide scores from 0.0 to 1.0:
1. correctness
2. relevance
3. completeness
4. clarity

Respond ONLY with valid JSON:
{{
    "correctness": 0.0,
    "relevance": 0.0,
    "completeness": 0.0,
    "clarity": 0.0,
    "reasoning": "brief explanation"
}}
"""

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = self.build_evaluation_prompt(
            question=question,
            reference_answer=reference_answer,
            student_answer=student_answer,
            grade_level=grade_level
        )

        try:
            result = await llm_client.chat_async(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are an expert {self.subject_name} "
                            "teacher. Always respond with valid JSON only."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.1
            )

            scores = self._parse_scores(result["text"])
            scores["model_used"] = result["model"]
            scores["provider"] = result["provider"]
            return scores

        except Exception as e:
            logger.warning(
                f"{self.subject_name} LLM evaluation failed: {e}"
            )
            return self._default_scores()

    def _parse_scores(self, response_text: str) -> Dict[str, Any]:
        try:
            json_match = re.search(
                r'\{[^{}]+\}',
                response_text,
                re.DOTALL
            )
            if json_match:
                data = json.loads(json_match.group())
                return {
                    "correctness": self._clamp(
                        data.get("correctness", 0.5)
                    ),
                    "relevance": self._clamp(
                        data.get("relevance", 0.5)
                    ),
                    "completeness": self._clamp(
                        data.get("completeness", 0.5)
                    ),
                    "clarity": self._clamp(
                        data.get("clarity", 0.5)
                    ),
                    "reasoning": data.get("reasoning", "")
                }
        except Exception as e:
            logger.warning(f"Score parsing failed: {e}")

        return self._default_scores()

    def _clamp(self, value: Any) -> float:
        try:
            v = float(value)
            if v > 1.0:
                v = v / 100.0
            return max(0.0, min(1.0, v))
        except (ValueError, TypeError):
            return 0.5

    def _default_scores(self) -> Dict[str, Any]:
        return {
            "correctness": 0.5,
            "relevance": 0.5,
            "completeness": 0.5,
            "clarity": 0.5,
            "reasoning": "Default scores - LLM evaluation failed",
            "model_used": "fallback",
            "provider": "none"
        }
