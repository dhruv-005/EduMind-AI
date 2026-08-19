from typing import Dict, Any, List, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client


class AnswerGenerator:
    """
    Generate model answers and marking schemes
    for generated questions.
    """

    async def generate_model_answer(
        self,
        question: str,
        subject: str,
        difficulty: str,
        marks: int,
        question_type: str,
        grade_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate model answer for a question.
        Returns answer text, key points, and marking scheme.
        """
        level_ctx = (
            f"Grade Level: {grade_level}" if grade_level else ""
        )

        prompt = f"""Generate a model answer for this {subject} question.

{level_ctx}
Question: {question}
Question Type: {question_type}
Difficulty: {difficulty}
Total Marks: {marks}

Provide:
1. A comprehensive model answer
2. Key points that must be mentioned (for partial marking)
3. A marking scheme showing how {marks} marks are distributed

Format:
MODEL_ANSWER: [complete answer here]
KEY_POINTS:
- [point 1 - X marks]
- [point 2 - X marks]
- [point 3 - X marks]
MARKING_SCHEME: [how marks are distributed]
"""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    f"You are an expert {subject} teacher. "
                    "Write clear, accurate model answers "
                    "appropriate for the grade level."
                ),
                max_tokens=800,
                temperature=0.3
            )

            return self._parse_answer_response(response, marks)

        except Exception as e:
            logger.warning(f"Answer generation failed: {e}")
            return {
                "model_answer": "Model answer not available.",
                "key_points": [],
                "marking_scheme": f"Full marks: {marks}"
            }

    def _parse_answer_response(
        self,
        response: str,
        marks: int
    ) -> Dict[str, Any]:
        """Parse the answer generation response."""
        model_answer = ""
        key_points = []
        marking_scheme = ""

        lines = response.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("MODEL_ANSWER:"):
                current_section = "answer"
                model_answer = line.replace(
                    "MODEL_ANSWER:", ""
                ).strip()
            elif line.startswith("KEY_POINTS:"):
                current_section = "points"
            elif line.startswith("MARKING_SCHEME:"):
                current_section = "scheme"
                marking_scheme = line.replace(
                    "MARKING_SCHEME:", ""
                ).strip()
            elif current_section == "answer" and line:
                model_answer += " " + line
            elif (
                current_section == "points" and
                line.startswith("-")
            ):
                point = line.lstrip("- ").strip()
                if point:
                    key_points.append(point)
            elif current_section == "scheme" and line:
                marking_scheme += " " + line

        return {
            "model_answer": model_answer.strip() or response[:500],
            "key_points": key_points[:10],
            "marking_scheme": marking_scheme.strip() or (
                f"Award {marks} marks for complete answer"
            )
        }

    async def generate_mcq_options(
        self,
        question: str,
        correct_answer: str,
        subject: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """
        Generate MCQ options for a question.
        Returns 4 options with correct answer identified.
        """
        prompt = f"""Generate 4 multiple choice options for this {subject} question.

Question: {question}
Correct Answer: {correct_answer}
Difficulty: {difficulty}

Rules:
- Option A should be the correct answer
- Options B, C, D should be plausible but incorrect (distractors)
- Distractors should be related but clearly wrong on examination
- All options should be similar in length

Format:
A) [correct answer]
B) [distractor 1]
C) [distractor 2]
D) [distractor 3]
CORRECT: A
"""

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "Generate clear, unambiguous MCQ options. "
                    "Distractors should be plausible but incorrect."
                ),
                max_tokens=300,
                temperature=0.5
            )

            return self._parse_mcq_options(response)

        except Exception as e:
            logger.warning(f"MCQ option generation failed: {e}")
            return {
                "options": [
                    correct_answer,
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "correct_option": "A"
            }

    def _parse_mcq_options(
        self,
        response: str
    ) -> Dict[str, Any]:
        """Parse MCQ options from response."""
        import re
        options = []
        correct = "A"

        for line in response.strip().split('\n'):
            line = line.strip()
            match = re.match(r'^([A-D])\)\s+(.+)', line)
            if match:
                options.append(match.group(2).strip())

            correct_match = re.search(
                r'CORRECT:\s*([A-D])',
                line
            )
            if correct_match:
                correct = correct_match.group(1)

        if len(options) < 4:
            while len(options) < 4:
                options.append(f"Option {chr(65 + len(options))}")

        return {
            "options": options[:4],
            "correct_option": correct
        }

    async def batch_generate_answers(
        self,
        questions: List[Dict[str, Any]],
        subject: str,
        grade_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate answers for a list of questions."""
        enriched = []

        for question in questions:
            try:
                answer_data = await self.generate_model_answer(
                    question=question["question_text"],
                    subject=subject,
                    difficulty=question.get("difficulty", "medium"),
                    marks=question.get("marks", 5),
                    question_type=question.get(
                        "question_type", "short"
                    ),
                    grade_level=grade_level
                )

                question["model_answer"] = (
                    answer_data["model_answer"]
                )
                question["key_points"] = (
                    answer_data["key_points"]
                )
                question["marking_scheme"] = (
                    answer_data["marking_scheme"]
                )

                # Generate MCQ options if needed
                if question.get("question_type") == "mcq":
                    mcq_data = await self.generate_mcq_options(
                        question=question["question_text"],
                        correct_answer=answer_data["model_answer"],
                        subject=subject,
                        difficulty=question.get("difficulty", "medium")
                    )
                    question["options"] = mcq_data["options"]
                    question["correct_option"] = (
                        mcq_data["correct_option"]
                    )

                enriched.append(question)

            except Exception as e:
                logger.error(
                    f"Failed to generate answer: {e}"
                )
                enriched.append(question)

        return enriched


# Singleton
answer_generator = AnswerGenerator()
