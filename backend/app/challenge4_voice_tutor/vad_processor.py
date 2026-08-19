import numpy as np
from typing import Optional, List, Tuple, Dict, Any
from app.core.logger import logger
from app.core.constants import (
    VAD_THRESHOLD,
    SILENCE_DURATION_MS,
    MIN_AUDIO_DURATION_S
)


class VADProcessor:
    """
    Voice Activity Detection processor.
    Uses Silero VAD for accurate speech detection.
    Detects when student starts/stops speaking.
    Also handles interruption detection.
    """

    def __init__(self):
        self._model = None
        self._utils = None
        self._sample_rate = 16000
        self._window_size_samples = 512

    def _load_silero_vad(self):
        """Load Silero VAD model lazily."""
        if self._model is None:
            try:
                import torch
                model, utils = torch.hub.load(
                    repo_or_dir='snakers4/silero-vad',
                    model='silero_vad',
                    force_reload=False,
                    trust_repo=True
                )
                self._model = model
                self._utils = utils
                logger.info("Silero VAD model loaded")
            except Exception as e:
                logger.warning(
                    f"Silero VAD failed to load: {e}. "
                    "Using energy-based VAD fallback."
                )
                self._model = None
        return self._model

    def detect_speech_energy(
        self,
        audio_chunk: bytes,
        threshold: float = 0.01
    ) -> bool:
        """
        Energy-based VAD fallback.
        Fast but less accurate than Silero.
        """
        try:
            audio_array = np.frombuffer(
                audio_chunk,
                dtype=np.int16
            ).astype(np.float32) / 32768.0

            # Calculate RMS energy
            energy = np.sqrt(np.mean(audio_array ** 2))
            return float(energy) > threshold

        except Exception as e:
            logger.debug(f"Energy VAD error: {e}")
            return False

    def detect_speech_silero(
        self,
        audio_chunk: bytes,
        sample_rate: int = 16000
    ) -> float:
        """
        Silero VAD speech probability detection.
        Returns probability 0.0-1.0 of speech present.
        """
        model = self._load_silero_vad()
        if not model:
            # Fallback to energy detection
            has_speech = self.detect_speech_energy(audio_chunk)
            return 0.9 if has_speech else 0.1

        try:
            import torch

            audio_array = np.frombuffer(
                audio_chunk,
                dtype=np.int16
            ).astype(np.float32) / 32768.0

            audio_tensor = torch.FloatTensor(audio_array)

            # Get speech probability
            speech_prob = model(
                audio_tensor,
                sample_rate
            ).item()

            return float(speech_prob)

        except Exception as e:
            logger.debug(f"Silero VAD error: {e}")
            has_speech = self.detect_speech_energy(audio_chunk)
            return 0.9 if has_speech else 0.1

    def is_speech(
        self,
        audio_chunk: bytes,
        threshold: float = VAD_THRESHOLD
    ) -> bool:
        """
        Check if audio chunk contains speech.
        Returns True if speech detected.
        """
        prob = self.detect_speech_silero(audio_chunk)
        return prob >= threshold

    def process_stream(
        self,
        audio_chunks: List[bytes],
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Process a stream of audio chunks.
        Returns speech segments and statistics.
        """
        speech_probs = []
        speech_segments = []
        in_speech = False
        speech_start = 0

        chunk_duration_ms = (
            len(audio_chunks[0]) / (sample_rate * 2) * 1000
            if audio_chunks else 0
        )

        for i, chunk in enumerate(audio_chunks):
            prob = self.detect_speech_silero(
                chunk, sample_rate
            )
            speech_probs.append(prob)

            is_speech = prob >= VAD_THRESHOLD

            if is_speech and not in_speech:
                in_speech = True
                speech_start = i

            elif not is_speech and in_speech:
                in_speech = False
                duration_ms = (
                    (i - speech_start) * chunk_duration_ms
                )
                if duration_ms >= MIN_AUDIO_DURATION_S * 1000:
                    speech_segments.append({
                        "start_chunk": speech_start,
                        "end_chunk": i,
                        "duration_ms": duration_ms
                    })

        # Handle ongoing speech at end
        if in_speech:
            speech_segments.append({
                "start_chunk": speech_start,
                "end_chunk": len(audio_chunks),
                "duration_ms": (
                    (len(audio_chunks) - speech_start) *
                    chunk_duration_ms
                )
            })

        total_speech_ms = sum(
            s["duration_ms"] for s in speech_segments
        )

        return {
            "speech_segments": speech_segments,
            "total_speech_ms": total_speech_ms,
            "avg_speech_prob": (
                sum(speech_probs) / len(speech_probs)
                if speech_probs else 0.0
            ),
            "has_speech": len(speech_segments) > 0
        }

    def detect_interruption(
        self,
        audio_chunk: bytes,
        is_tutor_speaking: bool,
        threshold: float = 0.6
    ) -> bool:
        """
        Detect if student is trying to interrupt tutor.
        Returns True if interruption detected.
        """
        if not is_tutor_speaking:
            return False

        # Higher threshold to avoid false positives
        prob = self.detect_speech_silero(audio_chunk)
        is_interrupting = prob >= threshold

        if is_interrupting:
            logger.info(
                f"Interruption detected "
                f"(prob={prob:.2f})"
            )

        return is_interrupting

    def get_audio_duration_ms(
        self,
        audio_bytes: bytes,
        sample_rate: int = 16000,
        bit_depth: int = 16
    ) -> float:
        """Calculate audio duration in milliseconds."""
        bytes_per_sample = bit_depth // 8
        num_samples = len(audio_bytes) / bytes_per_sample
        duration_s = num_samples / sample_rate
        return duration_s * 1000

    def remove_silence(
        self,
        audio_bytes: bytes,
        sample_rate: int = 16000,
        threshold: float = 0.005
    ) -> bytes:
        """
        Remove leading and trailing silence from audio.
        Returns trimmed audio bytes.
        """
        try:
            audio_array = np.frombuffer(
                audio_bytes,
                dtype=np.int16
            ).astype(np.float32) / 32768.0

            # Find speech boundaries
            energy = np.abs(audio_array)
            speech_mask = energy > threshold

            if not any(speech_mask):
                return audio_bytes

            first_speech = np.argmax(speech_mask)
            last_speech = len(speech_mask) - np.argmax(
                speech_mask[::-1]
            )

            # Add small buffer
            buffer = int(0.1 * sample_rate)
            start = max(0, first_speech - buffer)
            end = min(
                len(audio_array),
                last_speech + buffer
            )

            trimmed = audio_array[start:end]
            return (trimmed * 32768).astype(
                np.int16
            ).tobytes()

        except Exception as e:
            logger.debug(f"Silence removal failed: {e}")
            return audio_bytes


# Singleton
vad_processor = VADProcessor()
