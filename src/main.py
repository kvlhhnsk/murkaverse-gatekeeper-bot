"""
Murkaverse Gatekeeper Bot - Entry point.
Runs with long polling (no webhook required).
"""
import asyncio
import logging
import logging.handlers
import os
import signal
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramAPIError

from src.config import load_config
from src.db import Database
from src.handlers import start, lobby, join_requests, admin

# Configure logging - both console and file
LOG_DIR = os.getenv("LOG_DIR", "./logs")
LOG_FILE = Path(LOG_DIR) / "gatekeeper.log"

# Ensure log directory exists
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

# Set up handlers
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5 MB per file
    backupCount=3,  # Keep 3 backup files
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)  # More detail in file

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown (will be initialized in main)
shutdown_event: asyncio.Event | None = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    if shutdown_event:
        shutdown_event.set()


async def main() -> None:
    """Initialize and run the bot with automatic retry logic."""
    global shutdown_event
    
    logger.info("Starting Murkaverse Gatekeeper Bot...")
    
    # Initialize shutdown event in async context
    shutdown_event = asyncio.Event()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    try:
        config = load_config()
        logger.info(f"Config loaded. Group ID: {config.group_chat_id}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Initialize database with retry logic
    db = Database(config.sqlite_path)
    max_db_retries = 3
    db_retry_delay = 2
    
    for attempt in range(max_db_retries):
        try:
            await db.connect()
            logger.info(f"Database connected: {config.sqlite_path}")
            break
        except Exception as e:
            if attempt < max_db_retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_db_retries}): {e}. Retrying in {db_retry_delay}s...")
                await asyncio.sleep(db_retry_delay)
                db_retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Failed to connect to database after {max_db_retries} attempts: {e}")
                sys.exit(1)
    
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
    
    # Polling with automatic retry logic
    retry_count = 0
    max_retries = 10
    base_retry_delay = 5  # Start with 5 seconds
    
    while not shutdown_event.is_set():
        try:
            # Start polling (long polling, no webhook)
            await dp.start_polling(
                bot, 
                allowed_updates=[
                    "message",
                    "callback_query", 
                    "chat_join_request"
                ]
            )
            # If polling exits normally (shouldn't happen), break
            logger.info("Polling stopped normally")
            break
            
        except (TelegramNetworkError, ConnectionError, TimeoutError) as e:
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"Max retries ({max_retries}) reached. Shutting down.")
                break
            
            # Exponential backoff with jitter
            retry_delay = min(base_retry_delay * (2 ** (retry_count - 1)), 300)  # Cap at 5 minutes
            logger.warning(
                f"Network error (attempt {retry_count}/{max_retries}): {e}. "
                f"Retrying in {retry_delay}s..."
            )
            
            # Check if shutdown was requested during wait
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=retry_delay)
                logger.info("Shutdown requested during retry wait")
                break
            except asyncio.TimeoutError:
                pass  # Continue with retry
            
        except TelegramAPIError as e:
            # API errors might be permanent (e.g., invalid token)
            logger.error(f"Telegram API error: {e}")
            if "Unauthorized" in str(e) or "invalid" in str(e).lower():
                logger.error("Fatal API error - check bot token. Exiting.")
                break
            # For other API errors, retry with backoff
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"Max retries ({max_retries}) reached. Shutting down.")
                break
            retry_delay = min(base_retry_delay * (2 ** (retry_count - 1)), 300)
            logger.warning(f"API error (attempt {retry_count}/{max_retries}): {e}. Retrying in {retry_delay}s...")
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=retry_delay)
                break
            except asyncio.TimeoutError:
                pass
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            break
            
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error: {e}", exc_info=True)
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"Max retries ({max_retries}) reached due to unexpected errors. Shutting down.")
                break
            retry_delay = min(base_retry_delay * (2 ** (retry_count - 1)), 300)
            logger.warning(f"Unexpected error (attempt {retry_count}/{max_retries}). Retrying in {retry_delay}s...")
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=retry_delay)
                break
            except asyncio.TimeoutError:
                pass
    
    # Cleanup
    logger.info("Shutting down...")
    try:
        await db.close()
    except Exception as e:
        logger.warning(f"Error closing database: {e}")
    
    try:
        await bot.session.close()
    except Exception as e:
        logger.warning(f"Error closing bot session: {e}")
    
    logger.info("Shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)



