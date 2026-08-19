from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.logger import logger
from app.core.constants import DEFAULT_LANGUAGE


class ConversationManager:
    """
    Manage conversation history for voice tutor sessions.
    Maintains context window for LLM prompts.
    """

    MAX_HISTORY_TURNS = 20
    CONTEXT_WINDOW_TURNS = 10

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self,
        session_id: str,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        tutor_mode: str = "standard",
        language: str = DEFAULT_LANGUAGE
    ) -> Dict[str, Any]:
        """Create a new conversation session."""
        session = {
            "session_id": session_id,
            "subject": subject,
            "grade_level": grade_level,
            "tutor_mode": tutor_mode,
            "language": language,
            "history": [],
            "turn_count": 0,
            "topics_discussed": [],
            "detected_level": "intermediate",
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "is_active": True,
            "metadata": {}
        }

        self._sessions[session_id] = session
        logger.info(
            f"Conversation session created: {session_id} "
            f"subject={subject}"
        )
        return session

    def get_session(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get an existing session."""
        return self._sessions.get(session_id)

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self._sessions

    def add_turn(
        self,
        session_id: str,
        role: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Add a conversation turn to session history.
        Role: 'student' or 'tutor'
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(
                f"Session not found: {session_id}"
            )
            return {}

        session["turn_count"] += 1
        turn = {
            "turn_number": session["turn_count"],
            "role": role,
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        session["history"].append(turn)
        session["last_activity"] = (
            datetime.utcnow().isoformat()
        )

        # Trim history if too long
        if len(session["history"]) > self.MAX_HISTORY_TURNS:
            session["history"] = session["history"][
                -self.MAX_HISTORY_TURNS:
            ]

        # Track topics
        if role == "student" and metadata:
            topic = metadata.get("detected_topic")
            if topic and topic not in session["topics_discussed"]:
                session["topics_discussed"].append(topic)

        return turn

    def get_context_for_llm(
        self,
        session_id: str
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM.
        Returns last N turns as message list.
        """
        session = self._sessions.get(session_id)
        if not session:
            return []

        history = session["history"][-self.CONTEXT_WINDOW_TURNS:]
        messages = []

        for turn in history:
            role = (
                "user" if turn["role"] == "student"
                else "assistant"
            )
            messages.append({
                "role": role,
                "content": turn["text"]
            })

        return messages

    def update_detected_level(
        self,
        session_id: str,
        level: str
    ):
        """Update detected student level for session."""
        session = self._sessions.get(session_id)
        if session:
            session["detected_level"] = level

    def close_session(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Mark session as closed and return summary data."""
        session = self._sessions.get(session_id)
        if session:
            session["is_active"] = False
            session["closed_at"] = (
                datetime.utcnow().isoformat()
            )
            logger.info(
                f"Session closed: {session_id} "
                f"({session['turn_count']} turns)"
            )
        return session

    def get_session_stats(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get statistics for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return {}

        student_turns = [
            t for t in session["history"]
            if t["role"] == "student"
        ]
        tutor_turns = [
            t for t in session["history"]
            if t["role"] == "tutor"
        ]

        return {
            "session_id": session_id,
            "total_turns": session["turn_count"],
            "student_turns": len(student_turns),
            "tutor_turns": len(tutor_turns),
            "topics_discussed": session["topics_discussed"],
            "detected_level": session["detected_level"],
            "subject": session["subject"],
            "is_active": session["is_active"]
        }

    def cleanup_inactive_sessions(
        self,
        max_age_hours: int = 2
    ) -> int:
        """Remove old inactive sessions from memory."""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(
            hours=max_age_hours
        )
        to_remove = []

        for sid, session in self._sessions.items():
            last_activity = datetime.fromisoformat(
                session.get(
                    "last_activity",
                    datetime.utcnow().isoformat()
                )
            )
            if (
                not session["is_active"] and
                last_activity < cutoff
            ):
                to_remove.append(sid)

        for sid in to_remove:
            del self._sessions[sid]

        if to_remove:
            logger.info(
                f"Cleaned up {len(to_remove)} "
                f"inactive sessions"
            )

        return len(to_remove)


# Singleton
conversation_manager = ConversationManager()
