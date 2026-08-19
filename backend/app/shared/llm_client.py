import time
import asyncio
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import LLMException
from app.governance.model_fallback import model_fallback, FALLBACK_CHAIN


class LLMClient:
    """
    Unified LLM client with automatic fallback chain.
    Supports Groq, Gemini, Together AI, and Ollama.
    """

    def __init__(self):
        self._groq_client     = None
        self._gemini_client   = None
        self._together_client = None

    # ── GROQ ──────────────────────────────────────────────────────
    def _get_groq_client(self):
        """Initialize Groq client lazily."""
        if self._groq_client is None:
            try:
                from groq import Groq
                api_key = getattr(settings, 'GROQ_API_KEY', '').strip()
                if not api_key or api_key in (
                    'your_groq_api_key_here',
                    'gsk_your_groq_key_here',
                    'gsk_your_actual_groq_key_here',
                    ''
                ):
                    raise ValueError(
                        "GROQ_API_KEY not set in .env — "
                        "get free key at https://console.groq.com"
                    )
                self._groq_client = Groq(api_key=api_key)
                logger.info("Groq client initialized")
            except Exception as e:
                logger.error(f"Groq client init failed: {e}")
                raise
        return self._groq_client

    # ── GEMINI ────────────────────────────────────────────────────
    def _get_gemini_client(self):
        """Initialize Gemini client lazily."""
        if self._gemini_client is None:
            try:
                api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
                if not api_key or api_key in (
                    'your_gemini_api_key_here',
                    'your_gemini_key_here',
                    ''
                ):
                    raise ValueError(
                        "GEMINI_API_KEY not set in .env — "
                        "get free key at https://aistudio.google.com"
                    )

                model_name = getattr(
                    settings, 'GEMINI_MODEL', 'gemini-2.0-flash'
                )

                # Try new google-genai SDK first
                try:
                    from google import genai as google_genai
                    client = google_genai.Client(api_key=api_key)
                    self._gemini_client = {
                        "client": client,
                        "sdk":    "new",
                        "model":  model_name,
                    }
                    logger.info(
                        f"Gemini client initialized (new SDK) "
                        f"model={model_name}"
                    )

                except ImportError:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    model_obj = genai.GenerativeModel(model_name)
                    self._gemini_client = {
                        "client": model_obj,
                        "sdk":    "old",
                        "model":  model_name,
                    }
                    logger.info(
                        f"Gemini client initialized (legacy SDK) "
                        f"model={model_name}"
                    )

            except Exception as e:
                logger.error(f"Gemini client init failed: {e}")
                raise

        return self._gemini_client

    # ── GROQ CALL ─────────────────────────────────────────────────
    def _call_groq(
        self,
        messages:    List[Dict[str, str]],
        model:       str,
        max_tokens:  int   = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Call Groq API."""
        client   = self._get_groq_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=30,
        )
        return response.choices[0].message.content.strip()

    # ── GEMINI CALL ───────────────────────────────────────────────
    def _call_gemini(
        self,
        messages:    List[Dict[str, str]],
        model:       str,
        max_tokens:  int   = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Call Gemini API — supports new + old SDK."""
        gemini = self._get_gemini_client()
        sdk    = gemini["sdk"]
        client = gemini["client"]

        # Build prompt string
        prompt_parts = []
        for m in messages:
            role    = m.get("role", "user").lower()
            content = m.get("content", "")
            if role == "system":
                prompt_parts.append(f"Instructions: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(content)

        prompt = "\n\n".join(prompt_parts)

        if sdk == "new":
            from google import genai as google_genai
            from google.genai import types as genai_types

            response = client.models.generate_content(
                model=gemini["model"],
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text.strip()

        else:
            # Legacy SDK
            response = client.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature":       temperature,
                },
            )
            return response.text.strip()

    # ── TOGETHER CALL ─────────────────────────────────────────────
    def _call_together(
        self,
        messages:    List[Dict[str, str]],
        model:       str,
        max_tokens:  int   = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Call Together AI API."""
        import requests

        api_key = getattr(settings, 'TOGETHER_API_KEY', '').strip()
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not set in .env")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model":       model,
            "messages":    messages,
            "max_tokens":  max_tokens,
            "temperature": temperature,
        }
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        return (
            response.json()["choices"][0]["message"]["content"].strip()
        )

    # ── OLLAMA CALL ───────────────────────────────────────────────
    def _call_ollama(
        self,
        messages:    List[Dict[str, str]],
        model:       str,
        max_tokens:  int   = 2048,
        temperature: float = 0.3,
    ) -> str:
        """Call local Ollama API."""
        import requests

        prompt = "\n".join([
            f"{m['role'].upper()}: {m['content']}"
            for m in messages
        ])
        payload = {
            "model":  model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        response = requests.post(
            f"{getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')}"
            f"/api/generate",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["response"].strip()

    # ── MAIN CHAT ─────────────────────────────────────────────────
    def chat(
        self,
        messages:           List[Dict[str, str]],
        max_tokens:         int           = 4096,
        temperature:        float         = 0.3,
        preferred_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send chat with automatic fallback chain.
        Returns dict with text + metadata.
        """
        failed_providers: List[str] = []
        failed_models:    List[str] = []
        start_time = time.time()

        for model_config in FALLBACK_CHAIN:
            provider = model_config["provider"]
            model    = model_config["model"]

            # Skip already-failed providers
            if model in failed_models:
                continue

            # On first attempt, honour preferred_provider
            if preferred_provider and provider != preferred_provider:
                if not failed_providers:
                    continue

            try:
                logger.info(
                    f"Calling LLM: provider={provider}, model={model}"
                )

                if provider == "groq":
                    text = self._call_groq(
                        messages, model, max_tokens, temperature
                    )
                elif provider == "gemini":
                    text = self._call_gemini(
                        messages, model, max_tokens, temperature
                    )
                elif provider == "together":
                    text = self._call_together(
                        messages, model, max_tokens, temperature
                    )
                elif provider == "ollama":
                    text = self._call_ollama(
                        messages, model, max_tokens, temperature
                    )
                else:
                    logger.warning(f"Unknown provider: {provider}")
                    continue

                elapsed = (time.time() - start_time) * 1000
                model_fallback.mark_success(provider)

                logger.info(
                    f"LLM success: provider={provider} model={model} "
                    f"time={elapsed:.0f}ms tokens≈{len(text.split())}"
                )

                return {
                    "text":               text,
                    "provider":           provider,
                    "model":              model,
                    "processing_time_ms": elapsed,
                    "fallback_used":      bool(failed_providers),
                    "failed_providers":   failed_providers,
                }

            except ValueError as e:
                logger.error(
                    f"Provider {provider}/{model} config error: {e}"
                )
                failed_models.append(model)
                if provider not in failed_providers:
                    failed_providers.append(provider)
                continue

            except Exception as e:
                logger.warning(
                    f"Provider {provider}/{model} failed: {e}. "
                    f"Trying next..."
                )
                model_fallback.mark_failure(provider, str(e))
                failed_models.append(model)
                if provider not in failed_providers:
                    failed_providers.append(provider)
                continue

        raise LLMException(
            f"All LLM providers failed. "
            f"Failed: {failed_providers}. "
            f"Check API keys in .env and internet connection."
        )

    # ── ASYNC WRAPPER ─────────────────────────────────────────────
    async def chat_async(
        self,
        messages:    List[Dict[str, str]],
        max_tokens:  int   = 4096,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Async wrapper for chat()."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.chat(messages, max_tokens, temperature),
        )

    # ── SIMPLE PROMPT ─────────────────────────────────────────────
    def simple_prompt(
        self,
        prompt:      str,
        system:      str   = "You are a helpful AI assistant.",
        max_tokens:  int   = 2048,
        temperature: float = 0.3,
    ) -> str:
        """Single-turn prompt helper."""
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ]
        result = self.chat(messages, max_tokens, temperature)
        return result["text"]

    async def simple_prompt_async(
        self,
        prompt:      str,
        system:      str   = "You are a helpful AI assistant.",
        max_tokens:  int   = 2048,
        temperature: float = 0.3,
    ) -> str:
        """Async single-turn prompt helper."""
        result = await self.chat_async(
            [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            max_tokens,
            temperature,
        )
        return result["text"]

    # ── HEALTH CHECK ──────────────────────────────────────────────
    def health_check(self) -> Dict[str, Any]:
        """Test all providers and return status."""
        results       = {}
        test_messages = [{"role": "user", "content": "Say OK"}]

        seen_providers: List[str] = []
        for model_config in FALLBACK_CHAIN:
            provider = model_config["provider"]
            if provider in seen_providers:
                continue
            seen_providers.append(provider)

            try:
                result = self.chat(
                    test_messages,
                    max_tokens=10,
                    preferred_provider=provider,
                )
                results[provider] = {
                    "status":           "healthy",
                    "model":            model_config["model"],
                    "response_time_ms": result["processing_time_ms"],
                }
            except Exception as e:
                results[provider] = {
                    "status": "unhealthy",
                    "model":  model_config["model"],
                    "error":  str(e),
                }

        return results


# ── SINGLETON ─────────────────────────────────────────────────────
llm_client = LLMClient()
