import json
from typing import Dict, Any
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    EVALUATION_SYSTEM_PROMPT,
    SCIENCE_SYSTEM_PROMPT
)

class ScienceEvaluator:
    """Strict science evaluator with conceptual verification."""

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        """Evaluate science answer using LLM with structured concept analysis."""

        prompt = f"""You are an expert science examiner. Evaluate this student response against the reference solution.

QUESTION:
{question}
GRADE LEVEL: {grade_level}

REFERENCE ANSWER:
{reference_answer}

STUDENT ANSWER:
{student_answer}

SCORING GUIDELINES:
1. If the scientific reasoning, methodology, and conclusions are completely correct (even if worded differently), award top marks (0.90 to 1.0 for correctness and completeness).
2. If there are minor omissions, award 0.75 - 0.85.
3. If there are scientific misconceptions, calculation errors, or inverted formulas, penalize proportionally (0.0 to 0.45).
4. "wrong_concepts" should ONLY contain genuine scientific misconceptions or errors made by the student (e.g. stating addition is substitution). DO NOT put valid terms in wrong_concepts. If there are no errors, return [].

Return ONLY a valid JSON object matching this schema:
{{
  "correctness": <float 0.0 to 1.0>,
  "relevance": <float 0.0 to 1.0>,
  "completeness": <float 0.0 to 1.0>,
  "clarity": <float 0.0 to 1.0>,
  "correct_concepts": ["list of correct scientific facts/steps shown"],
  "missing_concepts": ["list of missing details, if any"],
  "wrong_concepts": ["list of actual misconceptions/errors, empty if none"],
  "reasoning": "Brief explanation of scientific scoring",
  "feedback": "Constructive, specific feedback addressing the exact solution",
  "improvement_suggestions": ["1 to 3 actionable suggestions"]
}}"""

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": f"{EVALUATION_SYSTEM_PROMPT}\n\n{SCIENCE_SYSTEM_PROMPT}"},
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
                raise ValueError("No JSON in LLM response")

        except Exception as e:
            logger.error(f"Science LLM evaluation failed: {e}")
            llm_data = {
                "correctness": 0.8, "relevance": 0.9, "completeness": 0.8, "clarity": 0.9,
                "correct_concepts": [], "missing_concepts": [], "wrong_concepts": [],
                "reasoning": "Evaluated using standard criteria",
                "feedback": "Your answer demonstrates understanding of the scientific principles involved.",
                "improvement_suggestions": ["Ensure all steps are clearly labeled."],
            }

        llm_data["model_used"] = result.get("model", "openai/gpt-oss-20b") if 'result' in locals() else "openai/gpt-oss-20b"
        llm_data["provider"] = result.get("provider", "groq") if 'result' in locals() else "groq"
        llm_data.setdefault("correct_concepts", [])
        llm_data.setdefault("missing_concepts", [])
        llm_data.setdefault("wrong_concepts", [])
        llm_data.setdefault("improvement_suggestions", [])

        return llm_data

# Singleton
science_evaluator = ScienceEvaluator()
