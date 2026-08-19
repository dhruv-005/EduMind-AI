import asyncio
import io
from typing import Optional, AsyncGenerator, Dict, Any
from app.core.logger import logger


class TTSEngine:
    """
    Text-to-Speech engine.
    Primary: Edge TTS (Microsoft, free, natural voices)
    Fallback: gTTS (Google, free)
    """

    # Available voices
    VOICES = {
        "en_female": "en-US-JennyNeural",
        "en_male": "en-US-GuyNeural",
        "en_female_uk": "en-GB-SoniaNeural",
        "en_male_uk": "en-GB-RyanNeural",
        "en_teacher": "en-US-AriaNeural"
    }

    DEFAULT_VOICE = "en-US-AriaNeural"

    def __init__(self):
        self._edge_available = None

    def _check_edge_tts(self) -> bool:
        """Check if edge-tts is available."""
        if self._edge_available is None:
            try:
                import edge_tts
                self._edge_available = True
                logger.info("Edge TTS available")
            except ImportError:
                self._edge_available = False
                logger.warning(
                    "edge-tts not installed. "
                    "Run: pip install edge-tts"
                )
        return self._edge_available

    async def synthesize_edge_tts(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ) -> bytes:
        """
        Synthesize speech using Edge TTS.
        Returns audio bytes (MP3).
        """
        try:
            import edge_tts

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch
            )

            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])

            audio_bytes = b"".join(audio_chunks)

            logger.info(
                f"Edge TTS: {len(text)} chars → "
                f"{len(audio_bytes)} bytes"
            )
            return audio_bytes

        except Exception as e:
            logger.warning(f"Edge TTS failed: {e}")
            raise

    async def synthesize_edge_tts_stream(
        self,
        text: str,
        voice: str = DEFAULT_VOICE
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio chunks from Edge TTS.
        Yields audio chunks as they're generated.
        First chunk arrives very quickly (< 200ms).
        """
        try:
            import edge_tts

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice
            )

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]

        except Exception as e:
            logger.warning(f"Edge TTS stream failed: {e}")
            # Yield empty to signal failure
            return

    def synthesize_gtts(
        self,
        text: str,
        language: str = "en"
    ) -> bytes:
        """
        Synthesize speech using gTTS (fallback).
        Returns audio bytes (MP3).
        """
        try:
            from gtts import gTTS
            import io

            tts = gTTS(text=text, lang=language, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()

            logger.info(
                f"gTTS: {len(text)} chars → "
                f"{len(audio_bytes)} bytes"
            )
            return audio_bytes

        except ImportError:
            logger.error(
                "gtts not installed. Run: pip install gtts"
            )
            raise
        except Exception as e:
            logger.error(f"gTTS failed: {e}")
            raise

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        language: str = "en",
        speed: str = "normal"
    ) -> Dict[str, Any]:
        """
        Synthesize speech with automatic fallback.
        Returns dict with audio_bytes and metadata.
        """
        if not text or not text.strip():
            return {
                "audio_bytes": b"",
                "provider": "none",
                "format": "mp3",
                "error": "Empty text"
            }

        # Limit text length
        text = text[:2000]

        # Set rate based on speed
        rate_map = {
            "slow": "-20%",
            "normal": "+0%",
            "fast": "+20%"
        }
        rate = rate_map.get(speed, "+0%")

        # Set voice
        selected_voice = voice or self.DEFAULT_VOICE

        # Try Edge TTS first
        if self._check_edge_tts():
            try:
                audio_bytes = await self.synthesize_edge_tts(
                    text=text,
                    voice=selected_voice,
                    rate=rate
                )
                return {
                    "audio_bytes": audio_bytes,
                    "provider": "edge_tts",
                    "voice": selected_voice,
                    "format": "mp3",
                    "text_length": len(text)
                }
            except Exception as e:
                logger.warning(
                    f"Edge TTS failed, trying gTTS: {e}"
                )

        # Fallback to gTTS
        try:
            audio_bytes = self.synthesize_gtts(
                text=text,
                language=language
            )
            return {
                "audio_bytes": audio_bytes,
                "provider": "gtts",
                "voice": f"gtts_{language}",
                "format": "mp3",
                "text_length": len(text)
            }
        except Exception as e:
            logger.error(f"All TTS engines failed: {e}")
            return {
                "audio_bytes": b"",
                "provider": "none",
                "format": "mp3",
                "error": str(e)
            }

    async def stream(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream TTS audio chunks.
        Use for real-time voice response.
        """
        selected_voice = voice or self.DEFAULT_VOICE

        if self._check_edge_tts():
            try:
                async for chunk in self.synthesize_edge_tts_stream(
                    text=text,
                    voice=selected_voice
                ):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"Stream TTS failed: {e}")

        # Fallback: synthesize all and yield in chunks
        try:
            result = await self.synthesize(text=text)
            audio_bytes = result.get("audio_bytes", b"")
            chunk_size = 4096
            for i in range(0, len(audio_bytes), chunk_size):
                yield audio_bytes[i:i + chunk_size]
        except Exception as e:
            logger.error(f"TTS stream fallback failed: {e}")

    def get_voice_for_subject(
        self,
        subject: Optional[str] = None
    ) -> str:
        """Get appropriate voice for subject."""
        return self.DEFAULT_VOICE

    def split_for_streaming(
        self,
        text: str,
        max_chunk: int = 100
    ) -> list:
        """
        Split long text into chunks for streaming TTS.
        Split at sentence boundaries for natural speech.
        """
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) < max_chunk:
                current += sentence + " "
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence + " "

        if current:
            chunks.append(current.strip())

        return chunks


# Singleton
tts_engine = TTSEngine()
