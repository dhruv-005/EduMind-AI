import uuid
import json
import re
from typing import List, Dict, Any, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client
from app.challenge2_generator.schemas import GeneratorConfig


class QuestionGenerator:
    """Generate exam questions using LLM."""

    def _build_generation_prompt(
        self,
        config: GeneratorConfig,
        pattern_context: Optional[Dict] = None,
        batch_size: int = 5
    ) -> str:
        """Build the question generation prompt."""
        topic_ctx = f"Topic: {config.topic}" if config.topic else ""
        level_ctx = f"Grade Level: {config.grade_level}" if config.grade_level else ""

        difficulty_instruction = {
            "easy":   "Create straightforward recall/definition questions",
            "medium": "Create application and understanding questions",
            "hard":   "Create analysis, evaluation and synthesis questions",
            "mixed":  "Mix easy (30%), medium (40%), and hard (30%) questions"
        }.get(config.difficulty, "Create varied difficulty questions")

        type_instruction = {
            "mcq":       "Generate multiple choice questions with 4 options",
            "short":     "Generate short answer questions (2-5 marks each)",
            "long":      "Generate detailed essay questions (10+ marks each)",
            "numerical": "Generate calculation questions",
            "mixed":     "Mix MCQ (30%), short (40%), long (20%), numerical (10%)"
        }.get(config.question_type, "Generate mixed question types")

        return f"""Generate exactly {batch_size} high-quality {config.subject} exam questions.

{level_ctx}
{topic_ctx}

Difficulty: {difficulty_instruction}
Question Type: {type_instruction}

CRITICAL RULES:
1. Return ONLY a valid JSON array - nothing else
2. Start with [ and end with ]
3. No markdown, no backticks, no code blocks
4. No comments inside JSON
5. Use only double quotes
6. Escape all special characters properly
7. No trailing commas

Return this exact format:
[
  {{
    "question_text": "Write the complete question here without any backslash characters",
    "question_type": "mcq",
    "difficulty": "medium",
    "topic": "topic name here",
    "marks": 5,
    "estimated_time_minutes": 5
  }}
]"""

    async def generate_batch(
        self,
        config: GeneratorConfig,
        pattern_context: Optional[Dict] = None,
        batch_size: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate a batch of questions."""
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
                            f"You are an expert {config.subject} exam paper setter. "
                            "Generate high-quality educational questions. "
                            "ALWAYS respond with a valid JSON array ONLY. "
                            "Never include markdown, backticks, or explanations. "
                            "Never use backslash characters in question text."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.5
            )

            questions = self._parse_questions(result["text"], config)

            for q in questions:
                q["id"]         = str(uuid.uuid4())
                q["subject"]    = config.subject
                q["grade_level"] = config.grade_level
                q["model_used"] = result.get("model", "")
                q["provider"]   = result.get("provider", "")

            logger.info(f"Generated {len(questions)} questions (batch_size={batch_size})")
            return questions

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return []

    def _clean_json_string(self, text: str) -> str:
        """Clean and fix common JSON issues from LLM responses."""
        if not text:
            return text

        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()

        # Fix invalid escape sequences
        # Replace \x where x is not a valid JSON escape char
        text = re.sub(r'\\([^"\\/bfnrtu])', lambda m: m.group(1), text)

        # Fix common issues
        text = text.replace('\t', ' ')
        text = text.replace('\r', '')

        return text

    def _parse_questions(
        self,
        response_text: str,
        config: GeneratorConfig
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into question list with multiple fallbacks."""

        if not response_text:
            return []

        # ── METHOD 1: Direct JSON parse after cleaning ─────────────
        try:
            cleaned = self._clean_json_string(response_text)
            start   = cleaned.find('[')
            end     = cleaned.rfind(']') + 1
            if start != -1 and end > start:
                json_str  = cleaned[start:end]
                questions = json.loads(json_str)
                if isinstance(questions, list) and len(questions) > 0:
                    logger.info(f"JSON parsed (method 1): {len(questions)} questions")
                    return [
                        self._normalize_question(q, config)
                        for q in questions
                        if isinstance(q, dict)
                    ]
        except Exception as e:
            logger.warning(f"Method 1 failed: {e}")

        # ── METHOD 2: Aggressive escape fixing ─────────────────────
        try:
            start = response_text.find('[')
            end   = response_text.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]

                # Remove all invalid escapes
                json_str = re.sub(r'\\([^"\\/bfnrtu0-9])', r'\1', json_str)

                # Fix newlines in strings
                json_str = re.sub(r'(?<!\\)\n', ' ', json_str)

                questions = json.loads(json_str)
                if isinstance(questions, list) and len(questions) > 0:
                    logger.info(f"JSON parsed (method 2): {len(questions)} questions")
                    return [
                        self._normalize_question(q, config)
                        for q in questions
                        if isinstance(q, dict)
                    ]
        except Exception as e:
            logger.warning(f"Method 2 failed: {e}")

        # ── METHOD 3: Extract individual JSON objects ───────────────
        try:
            questions = []
            # Find all {...} objects
            depth   = 0
            start_i = -1
            objects = []

            for i, ch in enumerate(response_text):
                if ch == '{':
                    if depth == 0:
                        start_i = i
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0 and start_i != -1:
                        objects.append(response_text[start_i:i+1])
                        start_i = -1

            for obj_str in objects:
                try:
                    cleaned = re.sub(r'\\([^"\\/bfnrtu0-9])', r'\1', obj_str)
                    obj     = json.loads(cleaned)
                    if isinstance(obj, dict) and (
                        'question_text' in obj or 'question' in obj
                    ):
                        questions.append(obj)
                except Exception:
                    continue

            if questions:
                logger.info(f"JSON parsed (method 3): {len(questions)} questions")
                return [
                    self._normalize_question(q, config)
                    for q in questions
                ]
        except Exception as e:
            logger.warning(f"Method 3 failed: {e}")

        # ── METHOD 4: Text extraction fallback ─────────────────────
        try:
            questions = self._extract_questions_fallback(response_text, config)
            if questions:
                logger.info(f"Extracted (method 4 text): {len(questions)} questions")
                return questions
        except Exception as e:
            logger.warning(f"Method 4 failed: {e}")

        # ── METHOD 5: Generate placeholder questions ────────────────
        logger.warning("All parse methods failed — generating placeholder questions")
        return self._generate_placeholder_questions(config)

    def _generate_placeholder_questions(
        self,
        config: GeneratorConfig,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate placeholder questions when LLM parsing fails."""
        topic   = config.topic or config.subject
        subject = config.subject

        templates = [
            f"Explain the concept of {topic} in {subject} with suitable examples.",
            f"What are the key principles of {topic}? Discuss in detail.",
            f"Compare and contrast the different aspects of {topic} in {subject}.",
            f"Define {topic} and explain its significance in {subject}.",
            f"Describe the process of {topic} and its applications.",
        ]

        questions = []
        for i in range(min(count, len(templates))):
            questions.append({
                "question_text":         templates[i],
                "question_type":         "short",
                "difficulty":            "medium",
                "topic":                 topic,
                "marks":                 config.marks_per_question or 5,
                "estimated_time_minutes": 10,
                "is_duplicate":          False,
            })

        return questions

    def _normalize_question(
        self,
        q: Dict[str, Any],
        config: GeneratorConfig
    ) -> Dict[str, Any]:
        """Normalize and validate a question dict."""
        valid_types        = ["mcq", "short", "long", "numerical"]
        valid_difficulties = ["easy", "medium", "hard"]

        # Get question text from various possible keys
        q_text = (
            q.get("question_text") or
            q.get("question") or
            q.get("text") or
            q.get("content") or
            ""
        )

        q_type = str(q.get("question_type", "short")).lower().strip()
        if q_type not in valid_types:
            q_type = "short"

        difficulty = str(q.get("difficulty", "medium")).lower().strip()
        if difficulty not in valid_difficulties:
            difficulty = "medium"

        marks = q.get("marks") or config.marks_per_question or 5
        try:
            marks = int(marks)
        except (ValueError, TypeError):
            marks = 5

        return {
            "question_text":         str(q_text).strip(),
            "question_type":         q_type,
            "difficulty":            difficulty,
            "topic":                 q.get("topic", config.topic or "general"),
            "marks":                 marks,
            "estimated_time_minutes": int(q.get("estimated_time_minutes", 5)),
            "model_answer":          q.get("model_answer", q.get("answer", "")),
            "options":               q.get("options", None),
            "correct_option":        q.get("correct_option", None),
            "is_duplicate":          False,
        }

    def _extract_questions_fallback(
        self,
        text: str,
        config: GeneratorConfig
    ) -> List[Dict[str, Any]]:
        """Fallback extraction when JSON parsing fails."""
        questions = []
        lines     = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match numbered questions: "1. " or "1) " or "Q1:"
            match = re.match(r'^(?:Q?\d+[.):\s]+)(.{20,})', line)
            if match:
                q_text = match.group(1).strip()
                if q_text and not q_text.startswith('{'):
                    questions.append({
                        "question_text":         q_text,
                        "question_type":         "short",
                        "difficulty":            "medium" if config.difficulty == "mixed" else config.difficulty,
                        "topic":                 config.topic or "general",
                        "marks":                 config.marks_per_question or 5,
                        "estimated_time_minutes": 5,
                        "is_duplicate":          False,
                    })

        return questions

    async def generate_all(
        self,
        config: GeneratorConfig,
        pattern_context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Generate all requested questions in batches."""
        all_questions = []
        remaining     = config.num_questions
        batch_size    = min(5, remaining)  # Smaller batches = better JSON

        while remaining > 0:
            current_batch = min(batch_size, remaining)

            batch = await self.generate_batch(
                config=config,
                pattern_context=pattern_context,
                batch_size=current_batch
            )

            if batch:
                all_questions.extend(batch)
                remaining -= current_batch
            else:
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
