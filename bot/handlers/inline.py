import asyncio
import logging

from aiogram import Bot, Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from bot.models import AVAILABLE_MODELS
from bot.providers.router import ProviderRouter
from bot.search.manager import SearchManager
from bot.tools import enhance_with_search

logger = logging.getLogger(__name__)

router = Router(name="inline")

# Use gemini-flash for fast inline responses
INLINE_MODEL = "gemini-flash"
INLINE_TIMEOUT = 12


@router.inline_query()
async def handle_inline_query(inline_query: InlineQuery, bot: Bot) -> None:
    """Handle inline queries."""
    query = (inline_query.query or "").strip()

    # If query is too short, return help
    if len(query) < 3:
        help_result = InlineQueryResultArticle(
            id="help",
            title="Type your question...",
            description="Enter at least 3 characters to get an AI response.",
            input_message_content=InputTextMessageContent(
                message_text="Please type a longer question to get an AI response."
            ),
        )
        await inline_query.answer([help_result], cache_time=5)
        return

    try:
        provider_router: ProviderRouter = bot["provider_router"]
        search_manager: SearchManager = bot["search_manager"]

        provider = provider_router.get_provider(INLINE_MODEL)
        actual_model_id = provider_router.get_model_id(INLINE_MODEL)

        # Enhance with search if needed
        search_context = await enhance_with_search(query, search_manager)
        messages = []
        if search_context:
            messages.append({"role": "system", "content": search_context})
        messages.append({"role": "user", "content": query})

        # Call LLM with timeout
        try:
            response_text = await asyncio.wait_for(
                provider.generate(messages, actual_model_id),
                timeout=INLINE_TIMEOUT,
            )
        except asyncio.TimeoutError:
            response_text = "Sorry, the request timed out. Please try again."

        # Truncate to Telegram's limit
        if len(response_text) > 4096:
            response_text = response_text[:4093] + "..."

        title = response_text[:60]
        description = response_text[:100]

        result = InlineQueryResultArticle(
            id="answer",
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(
                message_text=response_text
            ),
        )
        await inline_query.answer([result], cache_time=300)

    except Exception as e:
        logger.exception("Error processing inline query: %s", e)
        error_result = InlineQueryResultArticle(
            id="error",
            title="Error occurred",
            description="An error occurred while processing your query.",
            input_message_content=InputTextMessageContent(
                message_text="Sorry, an error occurred. Please try again."
            ),
        )
        await inline_query.answer([error_result], cache_time=5)
