import os
import tempfile
from typing import Optional, Dict, Any, Tuple
from app.core.logger import logger
from app.core.config import settings
from app.core.exceptions import FileProcessingException


class STTEngine:
    """
    Speech-to-Text engine.
    Primary: Groq Whisper API (fastest)
    Fallback: Local OpenAI Whisper
    """

    def __init__(self):
        self._local_model = None
        self._groq_client = None

    def _get_groq_client(self):
        """Get Groq client for Whisper API."""
        if self._groq_client is None:
            try:
                from groq import Groq
                self._groq_client = Groq(
                    api_key=settings.GROQ_API_KEY
                )
                logger.info("Groq STT client initialized")
            except Exception as e:
                logger.error(f"Groq STT init failed: {e}")
        return self._groq_client

    def _get_local_model(self):
        """Load local Whisper model lazily."""
        if self._local_model is None:
            try:
                import whisper
                self._local_model = whisper.load_model("base")
                logger.info("Local Whisper model loaded")
            except ImportError:
                logger.warning(
                    "openai-whisper not installed. "
                    "Run: pip install openai-whisper"
                )
            except Exception as e:
                logger.error(
                    f"Local Whisper load failed: {e}"
                )
        return self._local_model

    async def transcribe_groq(
        self,
        audio_bytes: bytes,
        language: str = "en",
        file_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio using Groq Whisper API.
        Returns transcript dict with text and metadata.
        """
        client = self._get_groq_client()
        if not client:
            raise FileProcessingException(
                "Groq STT client not available"
            )

        # Save audio to temp file
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_format}",
                delete=False
            ) as f:
                f.write(audio_bytes)
                temp_file = f.name

            with open(temp_file, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )

            result = {
                "text": transcription.text.strip(),
                "language": getattr(
                    transcription, 'language', language
                ),
                "duration": getattr(
                    transcription, 'duration', 0.0
                ),
                "confidence": 0.95,
                "provider": "groq_whisper",
                "segments": getattr(
                    transcription, 'segments', []
                )
            }

            logger.info(
                f"Groq STT: '{result['text'][:50]}...' "
                f"({result['duration']:.1f}s)"
            )
            return result

        except Exception as e:
            logger.warning(f"Groq STT failed: {e}")
            raise
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

    def transcribe_local(
        self,
        audio_bytes: bytes,
        language: str = "en",
        file_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio using local Whisper model.
        Fallback when Groq is unavailable.
        """
        model = self._get_local_model()
        if not model:
            raise FileProcessingException(
                "No STT engine available"
            )

        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_format}",
                delete=False
            ) as f:
                f.write(audio_bytes)
                temp_file = f.name

            result = model.transcribe(
                temp_file,
                language=language,
                fp16=False
            )

            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "duration": 0.0,
                "confidence": 0.85,
                "provider": "local_whisper",
                "segments": result.get("segments", [])
            }

        except Exception as e:
            logger.error(f"Local Whisper failed: {e}")
            raise FileProcessingException(
                f"STT failed: {str(e)}"
            )
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "en",
        file_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio with automatic fallback.
        Tries Groq first, then local Whisper.
        """
        if not audio_bytes or len(audio_bytes) < 100:
            return {
                "text": "",
                "language": language,
                "duration": 0.0,
                "confidence": 0.0,
                "provider": "none",
                "error": "Audio too short or empty"
            }

        # Try Groq first
        try:
            result = await self.transcribe_groq(
                audio_bytes=audio_bytes,
                language=language,
                file_format=file_format
            )
            return result
        except Exception as e:
            logger.warning(
                f"Groq STT failed, trying local: {e}"
            )

        # Fallback to local
        try:
            result = self.transcribe_local(
                audio_bytes=audio_bytes,
                language=language,
                file_format=file_format
            )
            return result
        except Exception as e:
            logger.error(f"All STT engines failed: {e}")
            return {
                "text": "",
                "language": language,
                "duration": 0.0,
                "confidence": 0.0,
                "provider": "none",
                "error": str(e)
            }

    def is_valid_audio(
        self,
        audio_bytes: bytes,
        min_duration_ms: int = 500,
        max_duration_ms: int = 30000
    ) -> Tuple[bool, str]:
        """
        Validate audio before transcription.
        Returns (is_valid, reason).
        """
        if not audio_bytes:
            return False, "Empty audio"

        # Rough size check (at 16kHz, 16bit = 32 bytes/ms)
        size_bytes = len(audio_bytes)
        estimated_ms = size_bytes / 32

        if estimated_ms < min_duration_ms:
            return False, f"Audio too short ({estimated_ms:.0f}ms)"

        if estimated_ms > max_duration_ms:
            return False, f"Audio too long ({estimated_ms:.0f}ms)"

        return True, "Valid"


# Singleton
stt_engine = STTEngine()
