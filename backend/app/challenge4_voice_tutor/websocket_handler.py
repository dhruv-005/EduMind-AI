import asyncio
import json
import base64
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from app.core.logger import logger
from app.challenge4_voice_tutor.stt_engine import stt_engine
from app.challenge4_voice_tutor.tts_engine import tts_engine
from app.challenge4_voice_tutor.vad_processor import vad_processor
from app.challenge4_voice_tutor.interrupt_handler import (
    interrupt_handler, TutorState
)
from app.challenge4_voice_tutor.service import (
    voice_tutor_service
)
from app.challenge4_voice_tutor.conversation_manager import (
    conversation_manager
)


class WebSocketHandler:
    """
    Handle WebSocket connections for voice tutor.
    Manages: audio streaming, interruption, STT, TTS.
    """

    async def handle_connection(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        """
        Main WebSocket connection handler.
        Manages the full conversation loop.
        """
        await websocket.accept()
        logger.info(
            f"WebSocket connected: {session_id[:8]}"
        )

        # Initialize session state
        interrupt_handler.set_state(
            session_id, TutorState.IDLE
        )
        stop_event = interrupt_handler.create_stop_event(
            session_id
        )

        # Get session info
        session = conversation_manager.get_session(session_id)
        subject = session.get("subject") if session else None
        grade_level = (
            session.get("grade_level") if session else None
        )
        tutor_mode = (
            session.get("tutor_mode", "standard")
            if session else "standard"
        )

        # Send welcome message
        await self._send_text_message(
            websocket=websocket,
            message_type="welcome",
            text=(
                f"Hello! I'm your AI tutor"
                f"{f' for {subject}' if subject else ''}. "
                "Start speaking and I'll help you learn!"
            ),
            session_id=session_id
        )

        # Send initial TTS greeting
        await self._send_tts_response(
            websocket=websocket,
            text=(
                f"Hello! I'm your AI tutor"
                f"{f' for {subject}' if subject else ''}. "
                "What would you like to learn today?"
            ),
            session_id=session_id,
            stop_event=stop_event
        )

        audio_buffer = []
        is_recording = False

        try:
            while True:
                try:
                    # Receive message from client
                    raw_message = await asyncio.wait_for(
                        websocket.receive(),
                        timeout=60.0
                    )
                except asyncio.TimeoutError:
                    # Send keepalive
                    await websocket.send_json({
                        "type": "keepalive",
                        "session_id": session_id
                    })
                    continue

                if "bytes" in raw_message:
                    # Audio chunk received
                    audio_chunk = raw_message["bytes"]

                    # Check for interruption
                    if interrupt_handler.is_speaking(
                        session_id
                    ):
                        is_speech = vad_processor.is_speech(
                            audio_chunk,
                            threshold=0.6
                        )
                        if is_speech:
                            await interrupt_handler.handle_interruption(
                                session_id=session_id
                            )
                            stop_event.set()
                            stop_event = (
                                interrupt_handler
                                .create_stop_event(session_id)
                            )

                            await self._send_status(
                                websocket,
                                session_id,
                                "interrupted",
                                "Listening..."
                            )
                            audio_buffer = []
                            is_recording = False
                            continue

                    # VAD processing
                    has_speech = vad_processor.is_speech(
                        audio_chunk
                    )

                    if has_speech and not is_recording:
                        is_recording = True
                        audio_buffer = []
                        interrupt_handler.set_state(
                            session_id,
                            TutorState.LISTENING
                        )
                        await self._send_status(
                            websocket, session_id,
                            "recording", "Recording..."
                        )

                    if is_recording:
                        audio_buffer.append(audio_chunk)

                    # Silence detection - end of speech
                    if not has_speech and is_recording:
                        silence_chunks = 0
                        for chunk in reversed(audio_buffer[-10:]):
                            if not vad_processor.is_speech(chunk):
                                silence_chunks += 1
                            else:
                                break

                        if silence_chunks >= 5:
                            # Process accumulated audio
                            is_recording = False
                            audio_data = b"".join(audio_buffer)
                            audio_buffer = []

                            if len(audio_data) > 1000:
                                await self._process_audio(
                                    websocket=websocket,
                                    session_id=session_id,
                                    audio_data=audio_data,
                                    subject=subject,
                                    grade_level=grade_level,
                                    tutor_mode=tutor_mode,
                                    stop_event=stop_event
                                )
                                stop_event = (
                                    interrupt_handler
                                    .create_stop_event(session_id)
                                )

                elif "text" in raw_message:
                    # JSON control message
                    try:
                        msg = json.loads(raw_message["text"])
                        await self._handle_control_message(
                            websocket=websocket,
                            session_id=session_id,
                            message=msg,
                            subject=subject,
                            grade_level=grade_level,
                            tutor_mode=tutor_mode,
                            stop_event=stop_event
                        )
                    except json.JSONDecodeError:
                        pass

        except WebSocketDisconnect:
            logger.info(
                f"WebSocket disconnected: {session_id[:8]}"
            )
        except Exception as e:
            logger.error(
                f"WebSocket error: {session_id[:8]} - {e}"
            )
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e),
                    "session_id": session_id
                })
            except Exception:
                pass
        finally:
            interrupt_handler.cleanup_session(session_id)
            logger.info(
                f"WebSocket cleanup: {session_id[:8]}"
            )

    async def _process_audio(
        self,
        websocket: WebSocket,
        session_id: str,
        audio_data: bytes,
        subject: Optional[str],
        grade_level: Optional[str],
        tutor_mode: str,
        stop_event: asyncio.Event
    ):
        """Process audio through STT → LLM → TTS pipeline."""
        interrupt_handler.set_state(
            session_id, TutorState.PROCESSING
        )
        await self._send_status(
            websocket, session_id,
            "processing", "Processing..."
        )

        # STT: Speech to text
        stt_result = await stt_engine.transcribe(
            audio_bytes=audio_data,
            language="en"
        )
        transcript = stt_result.get("text", "").strip()

        if not transcript:
            await self._send_status(
                websocket, session_id,
                "listening", "Could not hear clearly. Please try again."
            )
            interrupt_handler.set_state(
                session_id, TutorState.LISTENING
            )
            return

        # Send transcript to client
        await websocket.send_json({
            "type": "transcript",
            "session_id": session_id,
            "text": transcript,
            "confidence": stt_result.get("confidence", 0.9)
        })

        # LLM: Generate response
        response_data = (
            await voice_tutor_service.process_student_message(
                session_id=session_id,
                student_text=transcript,
                subject=subject,
                grade_level=grade_level,
                tutor_mode=tutor_mode
            )
        )

        response_text = response_data["response_text"]

        # Send text response
        await websocket.send_json({
            "type": "response",
            "session_id": session_id,
            "text": response_text,
            "metadata": {
                "detected_topic": response_data.get(
                    "detected_topic"
                ),
                "is_educational": response_data.get(
                    "is_educational", True
                ),
                "detected_level": response_data.get(
                    "detected_level"
                )
            }
        })

        # TTS: Text to speech
        await self._send_tts_response(
            websocket=websocket,
            text=response_text,
            session_id=session_id,
            stop_event=stop_event
        )

    async def _send_tts_response(
        self,
        websocket: WebSocket,
        text: str,
        session_id: str,
        stop_event: asyncio.Event
    ):
        """Stream TTS audio to client."""
        interrupt_handler.set_state(
            session_id, TutorState.SPEAKING
        )

        await websocket.send_json({
            "type": "tts_start",
            "session_id": session_id,
            "text_length": len(text)
        })

        try:
            chunk_count = 0
            async for audio_chunk in tts_engine.stream(text):
                if stop_event.is_set():
                    logger.info(
                        f"TTS stopped by interruption: "
                        f"{session_id[:8]}"
                    )
                    break

                # Send audio chunk as base64
                chunk_b64 = base64.b64encode(
                    audio_chunk
                ).decode()
                await websocket.send_json({
                    "type": "audio_chunk",
                    "session_id": session_id,
                    "data": chunk_b64,
                    "chunk_index": chunk_count
                })
                chunk_count += 1

        except Exception as e:
            logger.warning(f"TTS streaming error: {e}")
        finally:
            if not stop_event.is_set():
                interrupt_handler.set_state(
                    session_id, TutorState.LISTENING
                )
                await websocket.send_json({
                    "type": "tts_end",
                    "session_id": session_id
                })

    async def _handle_control_message(
        self,
        websocket: WebSocket,
        session_id: str,
        message: dict,
        subject: Optional[str],
        grade_level: Optional[str],
        tutor_mode: str,
        stop_event: asyncio.Event
    ):
        """Handle JSON control messages from client."""
        msg_type = message.get("type", "")

        if msg_type == "text_message":
            # Text input instead of voice
            text = message.get("text", "").strip()
            if text:
                response_data = (
                    await voice_tutor_service
                    .process_student_message(
                        session_id=session_id,
                        student_text=text,
                        subject=subject,
                        grade_level=grade_level,
                        tutor_mode=tutor_mode
                    )
                )
                await websocket.send_json({
                    "type": "response",
                    "session_id": session_id,
                    "text": response_data["response_text"]
                })

        elif msg_type == "interrupt":
            await interrupt_handler.handle_interruption(
                session_id=session_id
            )

        elif msg_type == "end_session":
            summary = (
                await voice_tutor_service
                .generate_session_summary(session_id)
            )
            await websocket.send_json({
                "type": "session_summary",
                "session_id": session_id,
                "summary": summary
            })

    async def _send_status(
        self,
        websocket: WebSocket,
        session_id: str,
        status: str,
        message: str = ""
    ):
        """Send status update to client."""
        try:
            await websocket.send_json({
                "type": "status",
                "session_id": session_id,
                "status": status,
                "message": message
            })
        except Exception:
            pass

    async def _send_text_message(
        self,
        websocket: WebSocket,
        message_type: str,
        text: str,
        session_id: str
    ):
        """Send text message to client."""
        try:
            await websocket.send_json({
                "type": message_type,
                "session_id": session_id,
                "text": text
            })
        except Exception:
            pass


# Singleton
websocket_handler = WebSocketHandler()
