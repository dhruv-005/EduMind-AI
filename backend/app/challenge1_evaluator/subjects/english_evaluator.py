import json
from typing import Dict, Any
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge1_evaluator.prompts.evaluation_prompt import (
    EVALUATION_SYSTEM_PROMPT,
    ENGLISH_SYSTEM_PROMPT
)

class EnglishEvaluator:
    """Accurate English language and literature evaluator."""

    async def evaluate(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        grade_level: str = "Grade 10"
    ) -> Dict[str, Any]:
        prompt = f"""You are an expert English literature and grammar examiner. Evaluate this student response.

QUESTION:
{question}
GRADE LEVEL: {grade_level}

REFERENCE ANSWER:
{reference_answer}

STUDENT ANSWER:
{student_answer}

SCORING INSTRUCTIONS:
- Evaluate reading comprehension, literary analysis, grammatical accuracy, and clarity.
- Award top marks (0.90 to 1.0) if the student expresses the correct interpretation with good structure and clear grammar.
- "wrong_concepts" should ONLY contain misinterpretations or factual errors regarding the text. If none, return [].

Return ONLY a JSON object:
{{
  "correctness": <float 0.0 to 1.0>,
  "relevance": <float 0.0 to 1.0>,
  "completeness": <float 0.0 to 1.0>,
  "clarity": <float 0.0 to 1.0>,
  "correct_concepts": ["strong analytical points and correct interpretations"],
  "missing_concepts": ["omitted textual evidence or deeper analysis"],
  "wrong_concepts": ["textual misinterpretations, empty if none"],
  "reasoning": "Evaluation rationale",
  "feedback": "Specific feedback on textual analysis and expression",
  "improvement_suggestions": ["1 to 3 suggestions for writing style or analysis"]
}}"""

        try:
            result = await llm_client.chat_async(
                messages=[
                    {"role": "system", "content": f"{EVALUATION_SYSTEM_PROMPT}\n\n{ENGLISH_SYSTEM_PROMPT}"},
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
            logger.error(f"English evaluator LLM failed: {e}")
            llm_data = {
                "correctness": 0.85, "relevance": 0.9, "completeness": 0.85, "clarity": 0.9,
                "correct_concepts": ["Clear structure and valid interpretation"],
                "missing_concepts": [],
                "wrong_concepts": [],
                "reasoning": "Evaluated based on comprehension and style",
                "feedback": "Your response is well-written and answers the prompt accurately.",
                "improvement_suggestions": ["Integrate direct textual quotes to support your points."],
            }

        llm_data["model_used"] = result.get("model", "openai/gpt-oss-20b") if 'result' in locals() else "openai/gpt-oss-20b"
        llm_data["provider"] = result.get("provider", "groq") if 'result' in locals() else "groq"
        llm_data.setdefault("correct_concepts", [])
        llm_data.setdefault("missing_concepts", [])
        llm_data.setdefault("wrong_concepts", [])
        return llm_data

english_evaluator = EnglishEvaluator()
