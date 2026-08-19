from typing import List, Dict, Any, Optional
from app.core.logger import logger
from app.shared.llm_client import llm_client


class FeedbackGenerator:
    """
    Generate human-readable feedback for student answers.
    Uses LLM to create encouraging and constructive feedback.
    """

    def _build_feedback_prompt(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        score: float,
        subject: str,
        missing_concepts: List[str],
        wrong_concepts: List[str],
        grade_level: Optional[str] = None
    ) -> str:
        """Build prompt for feedback generation."""
        level_context = (
            f"The student is in {grade_level}. " if grade_level else ""
        )
        missing_str = (
            ", ".join(missing_concepts[:5])
            if missing_concepts else "none"
        )
        wrong_str = (
            ", ".join(wrong_concepts[:3])
            if wrong_concepts else "none"
        )

        return f"""You are an expert {subject} teacher providing feedback on a student's answer.

{level_context}

Question: {question}

Reference Answer: {reference_answer[:500]}

Student's Answer: {student_answer[:500]}

Score: {score:.1f}/10

Missing concepts: {missing_str}
Wrong concepts: {wrong_str}

Write a feedback paragraph (3-4 sentences) that:
1. Acknowledges what the student got right
2. Points out what was missing or incorrect (be specific)
3. Gives encouragement and a clear direction to improve
4. Uses age-appropriate language

Then list 3 specific improvement suggestions as bullet points.

Format your response as:
FEEDBACK: [your feedback paragraph]
SUGGESTIONS:
- [suggestion 1]
- [suggestion 2]
- [suggestion 3]
"""

    async def generate_feedback(
        self,
        question: str,
        reference_answer: str,
        student_answer: str,
        score: float,
        subject: str,
        missing_concepts: List[str],
        wrong_concepts: List[str],
        grade_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate detailed feedback using LLM.
        Returns feedback text and improvement suggestions.
        """
        prompt = self._build_feedback_prompt(
            question=question,
            reference_answer=reference_answer,
            student_answer=student_answer,
            score=score,
            subject=subject,
            missing_concepts=missing_concepts,
            wrong_concepts=wrong_concepts,
            grade_level=grade_level
        )

        try:
            response = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "You are a supportive and expert teacher. "
                    "Provide constructive, encouraging feedback "
                    "that helps students learn and improve."
                ),
                max_tokens=600,
                temperature=0.4
            )

            return self._parse_feedback_response(response, score)

        except Exception as e:
            logger.warning(f"LLM feedback generation failed: {e}")
            return self._generate_fallback_feedback(
                score, missing_concepts, wrong_concepts
            )

    def _parse_feedback_response(
        self,
        response: str,
        score: float
    ) -> Dict[str, Any]:
        """Parse LLM feedback response into structured format."""
        feedback_text = ""
        suggestions = []

        try:
            lines = response.strip().split('\n')
            in_suggestions = False

            for line in lines:
                line = line.strip()
                if line.startswith("FEEDBACK:"):
                    feedback_text = line.replace(
                        "FEEDBACK:", ""
                    ).strip()
                elif line.startswith("SUGGESTIONS:"):
                    in_suggestions = True
                elif in_suggestions and line.startswith("-"):
                    suggestion = line.lstrip("- ").strip()
                    if suggestion:
                        suggestions.append(suggestion)
                elif not in_suggestions and line and not feedback_text:
                    feedback_text = line

            # If parsing failed, use full response as feedback
            if not feedback_text:
                feedback_text = response[:400]

        except Exception as e:
            logger.warning(f"Feedback parsing failed: {e}")
            feedback_text = response[:400] if response else (
                "Your answer has been evaluated."
            )

        return {
            "feedback": feedback_text,
            "improvement_suggestions": suggestions[:3]
        }

    def _generate_fallback_feedback(
        self,
        score: float,
        missing_concepts: List[str],
        wrong_concepts: List[str]
    ) -> Dict[str, Any]:
        """Generate template feedback when LLM fails."""
        if score >= 8.0:
            feedback = (
                "Excellent work! Your answer demonstrates a strong "
                "understanding of the topic. You have covered the "
                "key concepts effectively."
            )
        elif score >= 6.0:
            feedback = (
                "Good effort! Your answer covers some important "
                "points but could be more comprehensive. "
                "Review the missing concepts to improve your score."
            )
        elif score >= 4.0:
            feedback = (
                "Your answer shows partial understanding. "
                "You need to study the topic more thoroughly "
                "and include more key concepts in your response."
            )
        else:
            feedback = (
                "Your answer needs significant improvement. "
                "Please review the study material carefully "
                "and try to understand the core concepts."
            )

        suggestions = []
        if missing_concepts:
            suggestions.append(
                f"Study these missing concepts: "
                f"{', '.join(missing_concepts[:3])}"
            )
        if wrong_concepts:
            suggestions.append(
                f"Correct your understanding of: "
                f"{', '.join(wrong_concepts[:2])}"
            )
        suggestions.append(
            "Review your textbook and practice with similar questions."
        )

        return {
            "feedback": feedback,
            "improvement_suggestions": suggestions[:3]
        }

    def generate_subject_note(
        self,
        subject: str,
        score: float,
        missing_concepts: List[str]
    ) -> str:
        """Generate subject-specific note."""
        notes = {
            "mathematics": (
                "Remember to show all working steps clearly. "
                "Include units in your final answer."
                if score < 7
                else "Good mathematical reasoning shown."
            ),
            "science": (
                "Use correct scientific terminology. "
                "Explain cause and effect relationships clearly."
                if score < 7
                else "Good use of scientific concepts."
            ),
            "english": (
                "Focus on grammar, coherence, and argument structure. "
                "Support your points with evidence."
                if score < 7
                else "Good writing style and clarity."
            ),
            "general": (
                "Structure your answer with clear points. "
                "Address all parts of the question."
                if score < 7
                else "Well-structured response."
            )
        }
        return notes.get(subject.lower(), "")


# Singleton
feedback_generator = FeedbackGenerator()
