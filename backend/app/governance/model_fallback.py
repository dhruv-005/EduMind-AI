import time
from typing import Dict, Any, List
from app.core.logger import logger


# ── FALLBACK CHAIN ─────────────────────────────────────────────────
# Using only models available on this Groq account
FALLBACK_CHAIN = [
    {
        "provider":   "groq",
        "model":      "openai/gpt-oss-20b",
        "max_tokens": 4096,
        "priority":   1,
    },
    {
        "provider":   "groq",
        "model":      "qwen/qwen3.6-27b",
        "max_tokens": 4096,
        "priority":   2,
    },
    {
        "provider":   "groq",
        "model":      "groq/compound-mini",
        "max_tokens": 4096,
        "priority":   3,
    },
    {
        "provider":   "groq",
        "model":      "openai/gpt-oss-120b",
        "max_tokens": 4096,
        "priority":   4,
    },
    {
        "provider":   "gemini",
        "model":      "gemini-2.0-flash",
        "max_tokens": 4096,
        "priority":   5,
    },
]


class ModelFallbackManager:
    """
    Tracks provider health and failure counts.
    """

    def __init__(self):
        self._failures: Dict[str, int]   = {}
        self._successes: Dict[str, int]  = {}
        self._last_failure: Dict[str, float] = {}

    def mark_success(self, provider: str) -> None:
        self._successes[provider] = self._successes.get(provider, 0) + 1
        # Reset failure count on success
        self._failures[provider] = 0
        logger.debug(f"Provider {provider} marked successful")

    def mark_failure(self, provider: str, error: str = "") -> None:
        self._failures[provider] = self._failures.get(provider, 0) + 1
        self._last_failure[provider] = time.time()
        logger.warning(
            f"Provider {provider} failed "
            f"(count={self._failures[provider]}): {error}"
        )

    def get_failure_count(self, provider: str) -> int:
        return self._failures.get(provider, 0)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "failures":     self._failures,
            "successes":    self._successes,
            "last_failure": self._last_failure,
        }

    def reset(self, provider: str = None) -> None:
        if provider:
            self._failures.pop(provider, None)
            self._successes.pop(provider, None)
            self._last_failure.pop(provider, None)
        else:
            self._failures.clear()
            self._successes.clear()
            self._last_failure.clear()


# Singleton
model_fallback = ModelFallbackManager()
