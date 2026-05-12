import json
import logging
import re

from aiogram import Bot, F, Router
from aiogram.enums import ChatAction, ParseMode
from aiogram.types import CallbackQuery, Message

from bot.keyboards import model_selection_keyboard
from bot.models import AVAILABLE_MODELS
from bot.providers.router import ProviderRouter
from bot.search.manager import SearchManager
from bot.state import (
    add_to_history,
    clear_history,
    get_history,
    get_user_model,
    set_user_model,
)
from bot.tools import ToolExecutor, enhance_with_search, get_search_tool_schema

logger = logging.getLogger(__name__)

router = Router(name="dm")

# Model lookup by id
_MODEL_MAP = {m.id: m for m in AVAILABLE_MODELS}


@router.message(F.chat.type == "private", F.text == "/start")
async def cmd_start(message: Message) -> None:
    """Handle the /start command."""
    text = (
        "Hello! I'm an AI assistant powered by multiple LLM models.\n\n"
        "I can:\n"
        "- Chat with you using various AI models\n"
        "- Search the internet for current information\n"
        "- Switch between models on the fly\n\n"
        "Use /help to see available commands."
    )
    await message.answer(text)


@router.message(F.chat.type == "private", F.text == "/help")
async def cmd_help(message: Message) -> None:
    """Handle the /help command."""
    text = (
        "Available commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/model - Select AI model\n"
        "/clear - Clear conversation history\n"
        "/search <query> - Search the internet\n\n"
        "Just send me any message and I'll respond using the selected model."
    )
    await message.answer(text)


@router.message(F.chat.type == "private", F.text == "/model")
async def cmd_model(message: Message) -> None:
    """Handle the /model command - show model selection keyboard."""
    await message.answer(
        "Select a model:", reply_markup=model_selection_keyboard()
    )


@router.message(F.chat.type == "private", F.text == "/clear")
async def cmd_clear(message: Message) -> None:
    """Handle the /clear command - clear conversation history."""
    user_id = message.from_user.id  # type: ignore[union-attr]
    clear_history(user_id)
    await message.answer("Conversation history cleared.")


@router.message(F.chat.type == "private", F.text.startswith("/search"))
async def cmd_search(message: Message, bot: Bot) -> None:
    """Handle the /search command - perform explicit search."""
    query = (message.text or "").removeprefix("/search").strip()
    if not query:
        await message.answer("Usage: /search <query>")
        return

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    search_manager: SearchManager = bot["search_manager"]
    try:
        results = await search_manager.search(query)
        formatted = SearchManager.format_results(results)
        if formatted:
            await _send_long_message(message, formatted)
        else:
            await message.answer("No results found.")
    except Exception as e:
        logger.exception("Search error: %s", e)
        await message.answer("Sorry, an error occurred during search. Please try again.")


@router.callback_query(F.data.startswith("model:"))
async def on_model_selected(callback: CallbackQuery) -> None:
    """Handle model selection callback."""
    model_id = (callback.data or "").removeprefix("model:")
    if model_id not in _MODEL_MAP:
        await callback.answer("Unknown model.", show_alert=True)
        return

    user_id = callback.from_user.id
    set_user_model(user_id, model_id)
    model_name = _MODEL_MAP[model_id].name
    await callback.answer(f"Model set to {model_name}")
    if callback.message:
        await callback.message.edit_text(f"Model set to: {model_name}")  # type: ignore[union-attr]


@router.message(F.chat.type == "private", F.text)
async def handle_dm_message(message: Message, bot: Bot) -> None:
    """Handle general text messages in DM."""
    user_id = message.from_user.id  # type: ignore[union-attr]
    user_text = message.text or ""

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    try:
        model_id = get_user_model(user_id)
        model_info = _MODEL_MAP.get(model_id)
        if model_info is None:
            model_info = _MODEL_MAP[AVAILABLE_MODELS[0].id]
            model_id = model_info.id

        provider_router: ProviderRouter = bot["provider_router"]
        search_manager: SearchManager = bot["search_manager"]

        # Build messages from history
        history = get_history(user_id)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": user_text})

        # Add user message to history
        add_to_history(user_id, "user", user_text)

        provider = provider_router.get_provider(model_id)
        actual_model_id = provider_router.get_model_id(model_id)

        if model_info.supports_tools and model_info.provider == "google":
            # Gemini uses native google_search - no need to pass tool schema
            response_text = await provider.generate(messages, actual_model_id)
        elif model_info.supports_tools:
            # Fireworks models: pass tool schema and handle tool calls
            tools = [get_search_tool_schema()]
            response_text = await provider.generate(messages, actual_model_id, tools=tools)

            # Check if response contains tool calls (for Fireworks format)
            if "[Tool call: web_search(" in response_text:
                # Parse tool calls from the formatted response
                tool_calls = _parse_tool_calls(response_text)
                if tool_calls:
                    tool_executor = ToolExecutor(search_manager)
                    tool_results = await tool_executor.execute_tool_calls(tool_calls)

                    # Append the assistant tool-call message and tool results
                    messages.append({"role": "assistant", "content": response_text})
                    messages.extend(tool_results)

                    # Call the LLM again with tool results
                    response_text = await provider.generate(messages, actual_model_id, tools=tools)
        else:
            # Model doesn't support tools - use search enhancement
            search_context = await enhance_with_search(user_text, search_manager)
            if search_context:
                messages.insert(0, {"role": "system", "content": search_context})
            response_text = await provider.generate(messages, actual_model_id)

        # Add assistant response to history
        add_to_history(user_id, "assistant", response_text)

        # Send response (split if too long)
        await _send_long_message(message, response_text)

    except Exception as e:
        logger.exception("Error processing DM: %s", e)
        await message.answer("Sorry, an error occurred. Please try again.")


def _parse_tool_calls(response_text: str) -> list[dict]:
    """Parse tool calls from Fireworks-formatted response text.

    Expects format: [Tool call: web_search({"query": "..."})]
    """
    tool_calls = []
    pattern = r'\[Tool call: (\w+)\(({.*?})\)\]'
    matches = re.finditer(pattern, response_text, re.DOTALL)
    for i, match in enumerate(matches):
        name = match.group(1)
        args_str = match.group(2)
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            args = {}
        tool_calls.append({
            "id": f"call_{i}",
            "function": {
                "name": name,
                "arguments": json.dumps(args),
            },
        })
    return tool_calls


async def _send_long_message(message: Message, text: str) -> None:
    """Send a message, splitting into multiple if it exceeds Telegram's limit."""
    max_len = 4096
    if len(text) <= max_len:
        await message.answer(text)
        return

    # Split into chunks
    while text:
        chunk = text[:max_len]
        text = text[max_len:]
        await message.answer(chunk)
