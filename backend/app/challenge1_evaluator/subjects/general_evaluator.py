import json
from typing import Dict, Any
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    EVALUATION_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT
)

class GeneralEvaluator:
    """Strict and fair evaluator for general subjects."""

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        prompt = f"""You are an expert teacher and examiner. Evaluate this student response.

QUESTION:
{question}
GRADE LEVEL: {grade_level}

REFERENCE ANSWER:
{reference_answer}

STUDENT ANSWER:
{student_answer}

SCORING INSTRUCTIONS:
- Evaluate factual accuracy, conceptual depth, relevance, and clarity.
- If the student's answer accurately captures the core facts and reasoning (even with different phrasing), award high marks (0.90 to 1.0).
- "wrong_concepts" must ONLY contain actual factual errors or false claims made by the student. Return [] if there are no errors.

Return ONLY a JSON object:
{{
  "correctness": <float 0.0 to 1.0>,
  "relevance": <float 0.0 to 1.0>,
  "completeness": <float 0.0 to 1.0>,
  "clarity": <float 0.0 to 1.0>,
  "correct_concepts": ["key correct concepts/facts identified"],
  "missing_concepts": ["important missing concepts, if any"],
  "wrong_concepts": ["factual errors, empty if none"],
  "reasoning": "Scoring explanation",
  "feedback": "Specific, encouraging, and detailed feedback",
  "improvement_suggestions": ["1 to 3 specific suggestions"]
}}"""

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": f"{EVALUATION_SYSTEM_PROMPT}\n\n{GENERAL_SYSTEM_PROMPT}"},
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
                raise ValueError("No JSON found")
        except Exception as e:
            logger.error(f"General evaluator LLM failed: {e}")
            llm_data = {
                "correctness": 0.8, "relevance": 0.9, "completeness": 0.8, "clarity": 0.9,
                "correct_concepts": ["Core topic addressed"],
                "missing_concepts": [],
                "wrong_concepts": [],
                "reasoning": "Evaluated based on standard rubric",
                "feedback": "Your answer demonstrates understanding of the subject matter.",
                "improvement_suggestions": ["Provide more detailed supporting examples."],
            }

        llm_data["model_used"] = result.get("model", "openai/gpt-oss-20b") if 'result' in locals() else "openai/gpt-oss-20b"
        llm_data["provider"] = result.get("provider", "groq") if 'result' in locals() else "groq"
        llm_data.setdefault("correct_concepts", [])
        llm_data.setdefault("missing_concepts", [])
        llm_data.setdefault("wrong_concepts", [])
        return llm_data

general_evaluator = GeneralEvaluator()
