import asyncio
from typing import Optional, Callable, Any
from enum import Enum
from app.core.logger import logger


class TutorState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


class InterruptHandler:
    """
    Handle voice interruption state machine.
    Manages: IDLE → LISTENING → PROCESSING → SPEAKING → IDLE
    Handles interruption: SPEAKING → INTERRUPTED → LISTENING
    """

    def __init__(self):
        self._states: dict = {}
        self._audio_tasks: dict = {}
        self._stop_events: dict = {}

    def get_state(self, session_id: str) -> TutorState:
        """Get current state for session."""
        return self._states.get(session_id, TutorState.IDLE)

    def set_state(
        self,
        session_id: str,
        state: TutorState
    ):
        """Set state for session."""
        old_state = self._states.get(
            session_id, TutorState.IDLE
        )
        self._states[session_id] = state
        logger.debug(
            f"Session {session_id[:8]}: "
            f"{old_state} → {state}"
        )

    def is_speaking(self, session_id: str) -> bool:
        """Check if tutor is currently speaking."""
        return self.get_state(
            session_id
        ) == TutorState.SPEAKING

    def is_listening(self, session_id: str) -> bool:
        """Check if system is listening."""
        return self.get_state(
            session_id
        ) == TutorState.LISTENING

    def can_interrupt(self, session_id: str) -> bool:
        """Check if interruption is possible."""
        return self.get_state(
            session_id
        ) == TutorState.SPEAKING

    def create_stop_event(
        self,
        session_id: str
    ) -> asyncio.Event:
        """Create stop event for audio streaming."""
        event = asyncio.Event()
        self._stop_events[session_id] = event
        return event

    def get_stop_event(
        self,
        session_id: str
    ) -> Optional[asyncio.Event]:
        """Get stop event for session."""
        return self._stop_events.get(session_id)

    async def handle_interruption(
        self,
        session_id: str,
        on_interrupted: Optional[Callable] = None
    ) -> bool:
        """
        Handle student interruption while tutor is speaking.
        Stops audio, clears buffer, switches to listening.
        Returns True if interruption was handled.
        """
        if not self.can_interrupt(session_id):
            return False

        logger.info(
            f"Interruption handled: {session_id[:8]}"
        )

        # Set stop event to stop audio streaming
        stop_event = self._stop_events.get(session_id)
        if stop_event:
            stop_event.set()

        # Cancel audio task if running
        audio_task = self._audio_tasks.get(session_id)
        if audio_task and not audio_task.done():
            audio_task.cancel()
            try:
                await audio_task
            except asyncio.CancelledError:
                pass

        # Set interrupted state
        self.set_state(session_id, TutorState.INTERRUPTED)

        # Call callback if provided
        if on_interrupted:
            try:
                await on_interrupted(session_id)
            except Exception as e:
                logger.warning(
                    f"Interruption callback failed: {e}"
                )

        # Transition to listening
        await asyncio.sleep(0.1)
        self.set_state(session_id, TutorState.LISTENING)

        return True

    def register_audio_task(
        self,
        session_id: str,
        task: asyncio.Task
    ):
        """Register the current audio streaming task."""
        self._audio_tasks[session_id] = task

    def transition_to_listening(self, session_id: str):
        """Transition session to listening state."""
        self.set_state(session_id, TutorState.LISTENING)
        # Reset stop event
        self._stop_events[session_id] = asyncio.Event()

    def transition_to_speaking(self, session_id: str):
        """Transition session to speaking state."""
        self.set_state(session_id, TutorState.SPEAKING)

    def transition_to_processing(self, session_id: str):
        """Transition session to processing state."""
        self.set_state(session_id, TutorState.PROCESSING)

    def transition_to_idle(self, session_id: str):
        """Transition session to idle state."""
        self.set_state(session_id, TutorState.IDLE)

    def cleanup_session(self, session_id: str):
        """Clean up session resources."""
        self._states.pop(session_id, None)
        self._audio_tasks.pop(session_id, None)
        self._stop_events.pop(session_id, None)
        logger.debug(
            f"Interrupt handler cleaned up: {session_id[:8]}"
        )


# Singleton
interrupt_handler = InterruptHandler()
