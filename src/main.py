"""
Murkaverse Gatekeeper Bot - Entry point.
Runs with long polling (no webhook required).
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import load_config
from src.db import Database
from src.handlers import start, lobby, join_requests, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize and run the bot."""
    logger.info("Starting Murkaverse Gatekeeper Bot...")
    
    # Load configuration
    try:
        config = load_config()
        logger.info(f"Config loaded. Group ID: {config.group_chat_id}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Initialize database
    db = Database(config.sqlite_path)
    await db.connect()
    logger.info(f"Database connected: {config.sqlite_path}")
    
    # Initialize bot with default parse mode
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(start.router)
    dp.include_router(lobby.router)
    dp.include_router(join_requests.router)
    dp.include_router(admin.router)
    
    # Inject dependencies into handlers
    dp["db"] = db
    dp["config"] = config
    
    logger.info("Bot initialized, starting polling...")
    
    try:
        # Start polling (long polling, no webhook)
        await dp.start_polling(bot, allowed_updates=[
            "message",
            "callback_query", 
            "chat_join_request"
        ])
    finally:
        # Cleanup
        logger.info("Shutting down...")
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

