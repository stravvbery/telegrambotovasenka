import asyncio
import json
import logging
from typing import Any

import aiohttp

from bot.config import get_settings
from bot.providers import BaseLLMProvider

logger = logging.getLogger(__name__)

FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 60


class FireworksProvider(BaseLLMProvider):
    """LLM provider using the Fireworks AI OpenAI-compatible API."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._api_key = get_settings().fireworks_api_key
        self._session = session

    async def generate(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict] | None = None,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools

        for attempt in range(MAX_RETRIES):
            try:
                session = self._session
                owns_session = session is None
                if owns_session:
                    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
                    session = aiohttp.ClientSession(timeout=timeout)

                try:
                    async with session.post(
                        FIREWORKS_API_URL,
                        headers=headers,
                        json=payload,
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return self._extract_response(data)

                        error_text = await resp.text()
                        logger.warning(
                            "Fireworks API error (attempt %d/%d): %d %s",
                            attempt + 1,
                            MAX_RETRIES,
                            resp.status,
                            error_text,
                        )

                        if resp.status >= 500 or resp.status == 429:
                            backoff = 2**attempt
                            await asyncio.sleep(backoff)
                            continue

                        raise RuntimeError(
                            f"Fireworks API error: {resp.status} {error_text}"
                        )
                finally:
                    if owns_session:
                        await session.close()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(
                    "Fireworks request failed (attempt %d/%d): %s",
                    attempt + 1,
                    MAX_RETRIES,
                    str(e),
                )
                if attempt < MAX_RETRIES - 1:
                    backoff = 2**attempt
                    await asyncio.sleep(backoff)
                else:
                    raise RuntimeError(
                        f"Fireworks API request failed after {MAX_RETRIES} attempts: {e}"
                    ) from e

        raise RuntimeError(
            f"Fireworks API request failed after {MAX_RETRIES} attempts"
        )

    def _extract_response(self, data: dict) -> str:
        """Extract response text from the API response, handling tool_calls."""
        choice = data["choices"][0]
        message = choice["message"]

        # Handle tool_calls in the response
        if "tool_calls" in message and message["tool_calls"]:
            tool_calls = message["tool_calls"]
            parts = []
            for tool_call in tool_calls:
                func = tool_call.get("function", {})
                name = func.get("name", "unknown")
                args = func.get("arguments", "{}")
                try:
                    args_parsed = json.loads(args)
                    parts.append(
                        f"[Tool call: {name}({json.dumps(args_parsed)})]\n"
                    )
                except json.JSONDecodeError:
                    parts.append(f"[Tool call: {name}({args})]\n")
            # If there's also content, include it
            if message.get("content"):
                parts.append(message["content"])
            return "".join(parts)

        return message.get("content", "")
