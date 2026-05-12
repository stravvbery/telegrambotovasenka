import logging

from aiogram import Bot, Router
from aiogram.enums import ChatAction
from aiogram.types import Message

from bot.config import get_settings
from bot.models import AVAILABLE_MODELS
from bot.providers.router import ProviderRouter
from bot.search.manager import SearchManager
from bot.tools import enhance_with_search, get_search_tool_schema

logger = logging.getLogger(__name__)

router = Router(name="group")

_MODEL_MAP = {m.id: m for m in AVAILABLE_MODELS}


def _is_bot_mentioned(message: Message, bot_username: str) -> bool:
    """Check if the bot is mentioned in the message or if it's a reply to the bot."""
    # Check if message is a reply to bot
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.username == bot_username:
            return True

    # Check if bot is mentioned in text
    text = message.text or ""
    if f"@{bot_username}" in text:
        return True

    return False


@router.message()
async def handle_group_message(message: Message, bot: Bot) -> None:
    """Handle messages in group chats where bot is mentioned or replied to."""
    # Only process group/supergroup messages
    if message.chat.type not in ("group", "supergroup"):
        return

    # Only process text messages
    if not message.text:
        return

    bot_info = await bot.me()
    bot_username = bot_info.username or ""

    if not _is_bot_mentioned(message, bot_username):
        return

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    try:
        # Remove @mention from text
        query = message.text.replace(f"@{bot_username}", "").strip()
        if not query:
            await message.reply("Please include a message after mentioning me.")
            return

        settings = get_settings()
        model_id = settings.default_model
        model_info = _MODEL_MAP.get(model_id, AVAILABLE_MODELS[0])

        provider_router: ProviderRouter = bot["provider_router"]
        search_manager: SearchManager = bot["search_manager"]

        messages = [{"role": "user", "content": query}]
        provider = provider_router.get_provider(model_id)
        actual_model_id = provider_router.get_model_id(model_id)

        if model_info.supports_tools:
            tools = [get_search_tool_schema()]
            response_text = await provider.generate(messages, actual_model_id, tools=tools)
        else:
            search_context = await enhance_with_search(query, search_manager)
            if search_context:
                messages.insert(0, {"role": "system", "content": search_context})
            response_text = await provider.generate(messages, actual_model_id)

        # Reply to the triggering message, split if too long
        await _send_long_reply(message, response_text)

    except Exception as e:
        logger.exception("Error processing group message: %s", e)
        await message.reply("Sorry, an error occurred. Please try again.")


async def _send_long_reply(message: Message, text: str) -> None:
    """Reply to a message, splitting into multiple if it exceeds Telegram's limit."""
    max_len = 4096
    if len(text) <= max_len:
        await message.reply(text)
        return

    while text:
        chunk = text[:max_len]
        text = text[max_len:]
        await message.reply(chunk)
