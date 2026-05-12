import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import aiohttp

from bot.config import get_settings
from bot.providers import BaseLLMProvider

logger = logging.getLogger(__name__)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)
TIMEOUT_SECONDS = 60
RATE_LIMIT_COOLDOWN = 60.0
ERROR_COOLDOWN = 300.0
RECHECK_INTERVAL = 30.0


class KeyStatus(Enum):
    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


@dataclass
class KeyState:
    key: str
    status: KeyStatus = KeyStatus.HEALTHY
    last_used: float = 0.0
    cooldown_until: float = 0.0


class GeminiProvider(BaseLLMProvider):
    """LLM provider using Google Generative AI REST API with key rotation."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        settings = get_settings()
        self._keys: list[KeyState] = [
            KeyState(key=k) for k in settings.gemini_api_keys
        ]
        self._current_index: int = 0
        self._lock = asyncio.Lock()
        self._session = session

    def _get_next_key(self) -> KeyState | None:
        """Select the next healthy key using round-robin.

        Re-checks rate_limited and error keys if their cooldown has expired.
        """
        now = time.time()
        num_keys = len(self._keys)

        # First pass: re-enable keys whose cooldown expired
        for key_state in self._keys:
            if key_state.status in (KeyStatus.RATE_LIMITED, KeyStatus.ERROR):
                if now >= key_state.cooldown_until:
                    key_state.status = KeyStatus.HEALTHY

        # Round-robin among healthy keys
        for _ in range(num_keys):
            key_state = self._keys[self._current_index]
            self._current_index = (self._current_index + 1) % num_keys

            if key_state.status == KeyStatus.HEALTHY:
                key_state.last_used = now
                return key_state

        # If no healthy keys, try keys with expired cooldowns
        for key_state in self._keys:
            if key_state.status in (KeyStatus.RATE_LIMITED, KeyStatus.ERROR):
                if now >= key_state.cooldown_until:
                    key_state.status = KeyStatus.HEALTHY
                    key_state.last_used = now
                    return key_state

        return None

    def _mark_rate_limited(self, key_state: KeyState) -> None:
        """Mark a key as rate limited with cooldown."""
        key_state.status = KeyStatus.RATE_LIMITED
        key_state.cooldown_until = time.time() + RATE_LIMIT_COOLDOWN

    def _mark_error(self, key_state: KeyState) -> None:
        """Mark a key as having an error with a longer cooldown."""
        key_state.status = KeyStatus.ERROR
        key_state.cooldown_until = time.time() + ERROR_COOLDOWN

    async def generate(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict] | None = None,
    ) -> str:
        async with self._lock:
            key_state = self._get_next_key()

        if key_state is None:
            raise RuntimeError("No available Gemini API keys")

        url = GEMINI_API_URL.format(model=model)
        params = {"key": key_state.key}

        # Convert messages to Gemini format
        contents = self._convert_messages(messages)

        payload: dict[str, Any] = {"contents": contents}

        # Add google_search tool for grounding (ignore passed-in tools
        # since Gemini uses its native google_search instead)
        gemini_tools = self._build_tools()
        if gemini_tools:
            payload["tools"] = gemini_tools

        try:
            session = self._session
            owns_session = session is None
            if owns_session:
                timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
                session = aiohttp.ClientSession(timeout=timeout)

            try:
                async with session.post(
                    url,
                    params=params,
                    json=payload,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._extract_response(data)

                    error_text = await resp.text()
                    logger.warning(
                        "Gemini API error with key ...%s: %d %s",
                        key_state.key[-6:],
                        resp.status,
                        error_text,
                    )

                    if resp.status == 429 or resp.status >= 500:
                        self._mark_rate_limited(key_state)
                        raise RuntimeError(
                            f"Gemini API rate limited or server error: {resp.status}"
                        )

                    self._mark_error(key_state)
                    raise RuntimeError(
                        f"Gemini API error: {resp.status} {error_text}"
                    )
            finally:
                if owns_session:
                    await session.close()

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self._mark_rate_limited(key_state)
            raise RuntimeError(f"Gemini API request failed: {e}") from e

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert OpenAI-style messages to Gemini format.

        System messages are merged into the first user message to avoid
        consecutive same-role messages that Gemini rejects.
        """
        # Separate system content from other messages
        system_parts: list[str] = []
        non_system: list[dict] = []
        for msg in messages:
            if msg["role"] == "system":
                system_parts.append(msg["content"])
            else:
                non_system.append(msg)

        # If there's system content, prepend it to the first user message
        if system_parts and non_system:
            system_text = "\n".join(system_parts)
            for i, msg in enumerate(non_system):
                if msg["role"] == "user":
                    non_system[i] = {
                        "role": "user",
                        "content": system_text + "\n" + msg["content"],
                    }
                    break
            else:
                # No user message found; prepend as a user message
                non_system.insert(0, {"role": "user", "content": system_text})

        contents = []
        for msg in non_system:
            role = msg["role"]
            if role == "assistant":
                role = "model"

            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}],
            })
        return contents

    def _build_tools(self) -> list[dict]:
        """Build Gemini tools list with only the native google_search for grounding."""
        return [{"google_search": {}}]

    def _extract_response(self, data: dict) -> str:
        """Extract text from Gemini API response."""
        candidates = data.get("candidates", [])
        if not candidates:
            return ""

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        text_parts = []
        for part in parts:
            if "text" in part:
                text_parts.append(part["text"])

        return "".join(text_parts)
