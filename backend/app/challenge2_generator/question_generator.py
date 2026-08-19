import uuid
import json
import re
from typing import List, Dict, Any, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge2_generator.schemas import GeneratorConfig


class QuestionGenerator:
    """
    Generate exam questions using LLM.
    Uses patterns from source papers for better quality.
    """

    def _build_generation_prompt(
        self,
        config: GeneratorConfig,
        pattern_context: Optional[Dict] = None,
        batch_size: int = 5
    ) -> str:
        """Build the question generation prompt."""
        topic_ctx = (
            f"Topic: {config.topic}" if config.topic else ""
        )
        level_ctx = (
            f"Grade Level: {config.grade_level}"
            if config.grade_level else ""
        )
        pattern_ctx = ""
        if pattern_context:
            recurring = pattern_context.get(
                "recurring_topics", []
            )
            if recurring:
                pattern_ctx = (
                    f"Focus on these high-frequency topics: "
                    f"{', '.join(recurring[:5])}"
                )

        difficulty_instruction = {
            "easy": "Create straightforward recall/definition questions",
            "medium": "Create application and understanding questions",
            "hard": "Create analysis, evaluation and synthesis questions",
            "mixed": "Mix easy (30%), medium (40%), and hard (30%) questions"
        }.get(config.difficulty, "Create varied difficulty questions")

        type_instruction = {
            "mcq": "Generate multiple choice questions with 4 options",
            "short": "Generate short answer questions (2-5 marks each)",
            "long": "Generate detailed/essay questions (10+ marks each)",
            "numerical": "Generate calculation/numerical questions",
            "mixed": "Mix MCQ (30%), short (40%), long (20%), numerical (10%)"
        }.get(config.question_type, "Generate mixed question types")

        return f"""Generate {batch_size} high-quality {config.subject} exam questions.

{level_ctx}
{topic_ctx}
{pattern_ctx}

Difficulty: {difficulty_instruction}
Question Type: {type_instruction}
Marks per question: approximately {config.marks_per_question}

Requirements:
- Questions must be clear, unambiguous, and educationally valid
- Cover different aspects of the subject
- Be appropriate for the grade level
- Avoid repetition between questions
- Use proper academic language

Return ONLY a valid JSON array:
[
  {{
    "question_text": "The complete question text here",
    "question_type": "mcq/short/long/numerical",
    "difficulty": "easy/medium/hard",
    "topic": "specific topic name",
    "marks": 5,
    "estimated_time_minutes": 5
  }}
]
"""

    async def generate_batch(
        self,
        config: GeneratorConfig,
        pattern_context: Optional[Dict] = None,
        batch_size: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of questions.
        Returns list of question dicts.
        """
        prompt = self._build_generation_prompt(
            config=config,
            pattern_context=pattern_context,
            batch_size=batch_size
        )

        try:
            result = await llm_client.chat_async(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are an expert {config.subject} "
                            "exam paper setter with 20 years experience. "
                            "Generate high-quality educational questions. "
                            "Always respond with valid JSON array only."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )

            questions = self._parse_questions(
                result["text"], config
            )

            # Add metadata
            for q in questions:
                q["id"] = str(uuid.uuid4())
                q["subject"] = config.subject
                q["grade_level"] = config.grade_level
                q["model_used"] = result["model"]
                q["provider"] = result["provider"]

            logger.info(
                f"Generated {len(questions)} questions "
                f"(batch_size={batch_size})"
            )
            return questions

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return []

    def _parse_questions(
        self,
        response_text: str,
        config: GeneratorConfig
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into question list."""
        try:
            # Find JSON array in response
            array_match = re.search(
                r'\[.+\]',
                response_text,
                re.DOTALL
            )
            if array_match:
                questions = json.loads(array_match.group())
                if isinstance(questions, list):
                    return [
                        self._normalize_question(q, config)
                        for q in questions
                        if isinstance(q, dict)
                        and q.get("question_text")
                    ]
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}")

        # Fallback: extract question texts manually
        return self._extract_questions_fallback(
            response_text, config
        )

    def _normalize_question(
        self,
        q: Dict[str, Any],
        config: GeneratorConfig
    ) -> Dict[str, Any]:
        """Normalize and validate a question dict."""
        valid_types = ["mcq", "short", "long", "numerical"]
        valid_difficulties = ["easy", "medium", "hard"]

        q_type = q.get("question_type", "short").lower()
        if q_type not in valid_types:
            q_type = "short"

        difficulty = q.get("difficulty", "medium").lower()
        if difficulty not in valid_difficulties:
            difficulty = "medium"

        return {
            "question_text": str(
                q.get("question_text", "")
            ).strip(),
            "question_type": q_type,
            "difficulty": difficulty,
            "topic": q.get("topic", config.topic or "general"),
            "marks": int(q.get(
                "marks", config.marks_per_question or 5
            )),
            "estimated_time_minutes": int(
                q.get("estimated_time_minutes", 5)
            ),
            "is_duplicate": False
        }

    def _extract_questions_fallback(
        self,
        text: str,
        config: GeneratorConfig
    ) -> List[Dict[str, Any]]:
        """Fallback extraction when JSON parsing fails."""
        questions = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Look for numbered questions
            match = re.match(r'^\d+[.)]\s+(.+)', line)
            if match and len(match.group(1)) > 15:
                questions.append({
                    "question_text": match.group(1).strip(),
                    "question_type": "short",
                    "difficulty": config.difficulty
                    if config.difficulty != "mixed" else "medium",
                    "topic": config.topic or "general",
                    "marks": config.marks_per_question or 5,
                    "estimated_time_minutes": 5,
                    "is_duplicate": False
                })

        return questions

    async def generate_all(
        self,
        config: GeneratorConfig,
        pattern_context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate all requested questions.
        Splits into batches for better quality.
        """
        all_questions = []
        remaining = config.num_questions
        batch_size = min(10, remaining)

        while remaining > 0:
            current_batch = min(batch_size, remaining)

            batch = await self.generate_batch(
                config=config,
                pattern_context=pattern_context,
                batch_size=current_batch
            )

            all_questions.extend(batch)
            remaining -= current_batch

            if not batch:
                logger.warning(
                    f"Empty batch returned, stopping. "
                    f"Generated {len(all_questions)} so far."
                )
                break

        logger.info(
            f"Total questions generated: {len(all_questions)} "
            f"(requested: {config.num_questions})"
        )

        return all_questions[:config.num_questions]


# Singleton
question_generator = QuestionGenerator()
