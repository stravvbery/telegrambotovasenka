import logging

import aiohttp
from aiogram import Bot, Dispatcher

from bot.config import get_settings
from bot.handlers.dm import router as dm_router
from bot.handlers.group import router as group_router
from bot.handlers.inline import router as inline_router
from bot.providers.router import ProviderRouter
from bot.search.manager import SearchManager

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    settings = get_settings()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Initialize shared resources
    search_manager = SearchManager(settings)

    # Register routers
    dp.include_router(dm_router)
    dp.include_router(group_router)
    dp.include_router(inline_router)

    # Startup hook - create aiohttp session and initialize providers
    @dp.startup()
    async def on_startup() -> None:
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        bot["session"] = session
        bot["search_manager"] = search_manager
        bot["provider_router"] = ProviderRouter(session=session)
        logger.info("Bot started")

    # Shutdown hook - close aiohttp session
    @dp.shutdown()
    async def on_shutdown() -> None:
        session: aiohttp.ClientSession = bot["session"]
        await session.close()
        logger.info("Bot stopped")

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
