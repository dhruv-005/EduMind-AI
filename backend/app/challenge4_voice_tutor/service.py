import time
from typing import Dict, Any, Optional, List
from app.core.logger import logger
from app.core.config import settings
from app.shared.llm_client import llm_client
from app.challenge4_voice_tutor.topic_guard import topic_guard
from app.challenge4_voice_tutor.level_detector import (
    level_detector
)
from app.challenge4_voice_tutor.hint_engine import hint_engine
from app.challenge4_voice_tutor.conversation_manager import (
    conversation_manager
)
from app.governance.content_filter import content_filter
from app.governance.bias_detector import bias_detector
from app.governance.prompt_versioning import prompt_versioning
from app.challenge4_voice_tutor.prompts.tutor_system_prompt import (
    build_tutor_system_prompt
)


class VoiceTutorService:
    """
    Core service for Challenge 4 - Voice AI Tutor.
    Handles question processing and response generation.
    """

    async def process_student_message(
        self,
        session_id: str,
        student_text: str,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        tutor_mode: str = "standard"
    ) -> Dict[str, Any]:
        """
        Process student's message and generate tutor response.
        Returns response dict with text and metadata.
        """
        start_time = time.time()

        # Get session
        session = conversation_manager.get_session(session_id)
        if not session:
            session = conversation_manager.create_session(
                session_id=session_id,
                subject=subject,
                grade_level=grade_level,
                tutor_mode=tutor_mode
            )

        effective_subject = (
            subject or
            session.get("subject") or
            "general"
        )
        effective_grade = (
            grade_level or
            session.get("grade_level")
        )

        # STEP 1: Topic guard check
        guard_result = await topic_guard.check(
            text=student_text,
            session_subject=effective_subject
        )

        if guard_result["should_reject"]:
            rejection = guard_result["rejection_message"]

            # Add to history
            conversation_manager.add_turn(
                session_id=session_id,
                role="student",
                text=student_text,
                metadata={
                    "is_educational": False,
                    "topic_rejected": True
                }
            )
            conversation_manager.add_turn(
                session_id=session_id,
                role="tutor",
                text=rejection,
                metadata={"is_rejection": True}
            )

            elapsed_ms = (time.time() - start_time) * 1000
            return {
                "response_text": rejection,
                "is_educational": False,
                "topic_rejected": True,
                "detected_topic": guard_result.get(
                    "detected_topic"
                ),
                "processing_time_ms": elapsed_ms,
                "model_used": "none",
                "provider": "none"
            }

        # STEP 2: Level detection
        history = conversation_manager.get_context_for_llm(
            session_id
        )
        level_result = level_detector.detect_level(
            text=student_text,
            conversation_history=session.get("history", [])
        )
        conversation_manager.update_detected_level(
            session_id,
            level_result["detected_level"]
        )

        # STEP 3: Check if hint mode needed
        use_hints = (
            tutor_mode == "hint_mode" or
            hint_engine.should_use_hint_mode(student_text)
        )

        if use_hints and tutor_mode == "hint_mode":
            hint_result = await hint_engine.generate_hint(
                question=student_text,
                student_attempt=student_text,
                subject=effective_subject,
                hint_level=0,
                grade_level=effective_grade
            )
            response_text = hint_result["hint"]
        elif tutor_mode == "socratic":
            # Generate Socratic response
            response_text = await self._generate_socratic_response(
                student_text=student_text,
                subject=effective_subject,
                history=history,
                level=level_result["detected_level"],
                grade_level=effective_grade
            )
        else:
            # Standard tutoring response
            response_text, llm_meta = (
                await self._generate_standard_response(
                    student_text=student_text,
                    subject=effective_subject,
                    history=history,
                    level=level_result,
                    grade_level=effective_grade
                )
            )

        # STEP 4: Content filter on response
        output_status, _, _ = content_filter.check_output(
            response_text
        )

        # STEP 5: Add to history
        conversation_manager.add_turn(
            session_id=session_id,
            role="student",
            text=student_text,
            metadata={
                "is_educational": True,
                "detected_topic": guard_result.get(
                    "detected_topic"
                ),
                "level": level_result["detected_level"]
            }
        )
        conversation_manager.add_turn(
            session_id=session_id,
            role="tutor",
            text=response_text,
            metadata={
                "tutor_mode": tutor_mode,
                "governance_status": output_status
            }
        )

        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "response_text": response_text,
            "is_educational": True,
            "topic_rejected": False,
            "detected_topic": guard_result.get(
                "detected_topic"
            ),
            "detected_level": level_result["detected_level"],
            "question_type": level_result["question_type"],
            "tutor_mode": tutor_mode,
            "processing_time_ms": elapsed_ms,
            "model_used": settings.GROQ_MODEL,
            "provider": "groq",
            "governance_status": output_status
        }

    async def _generate_standard_response(
        self,
        student_text: str,
        subject: str,
        history: List[Dict],
        level: Dict[str, Any],
        grade_level: Optional[str]
    ) -> tuple:
        """Generate standard tutoring response."""
        system_prompt = build_tutor_system_prompt(
            subject=subject,
            grade_level=grade_level,
            detected_level=level["detected_level"],
            guidelines=level.get("response_guidelines", {})
        )

        messages = [
            {"role": "system", "content": system_prompt}
        ] + history + [
            {"role": "user", "content": student_text}
        ]

        result = await llm_client.chat_async(
            messages=messages,
            max_tokens=400,
            temperature=0.5
        )

        return result["text"], result

    async def _generate_socratic_response(
        self,
        student_text: str,
        subject: str,
        history: List[Dict],
        level: str,
        grade_level: Optional[str]
    ) -> str:
        """Generate Socratic questioning response."""
        system = (
            f"You are a Socratic {subject} tutor. "
            "Never directly answer questions. "
            "Instead, ask guiding questions that lead "
            "the student to discover the answer themselves. "
            "Be patient, encouraging, and use examples. "
            f"Adjust complexity for {level} level student."
        )

        messages = [
            {"role": "system", "content": system}
        ] + history + [
            {"role": "user", "content": student_text}
        ]

        result = await llm_client.chat_async(
            messages=messages,
            max_tokens=200,
            temperature=0.6
        )

        return result["text"]

    async def generate_session_summary(
        self,
        session_id: str
    ) -> str:
        """Generate a summary of the tutoring session."""
        stats = conversation_manager.get_session_stats(
            session_id
        )
        history = conversation_manager.get_context_for_llm(
            session_id
        )

        topics = stats.get("topics_discussed", [])
        topics_str = (
            ", ".join(topics) if topics else "various topics"
        )

        prompt = (
            f"Summarize this tutoring session in 3 sentences:\n"
            f"- Subject: {stats.get('subject', 'general')}\n"
            f"- Topics covered: {topics_str}\n"
            f"- Total turns: {stats.get('total_turns', 0)}\n"
            f"- Student level: {stats.get('detected_level')}\n"
            f"Focus on what was learned and next steps."
        )

        try:
            summary = await llm_client.simple_prompt_async(
                prompt=prompt,
                system=(
                    "Generate a brief, encouraging "
                    "session summary for the student."
                ),
                max_tokens=200,
                temperature=0.4
            )
            return summary
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            return (
                f"Great session! You covered {topics_str} "
                f"with {stats.get('total_turns', 0)} exchanges. "
                "Keep practicing!"
            )


# Singleton
voice_tutor_service = VoiceTutorService()
