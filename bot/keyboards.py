from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.models import AVAILABLE_MODELS


def model_selection_keyboard() -> InlineKeyboardMarkup:
    """Build an inline keyboard with one button per available model."""
    builder = InlineKeyboardBuilder()
    for model in AVAILABLE_MODELS:
        builder.button(text=model.name, callback_data=f"model:{model.id}")
    builder.adjust(1)
    return builder.as_markup()
