"""
Handler for /start command and deep links.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject

from src import texts, keyboards
from src.db import Database

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart(deep_link=True))
async def start_deep_link(message: Message, command: CommandObject, db: Database) -> None:
    """Handle /start with deep link (e.g., ?start=join)."""
    user_id = message.from_user.id
    logger.info(f"User {user_id} started with deep link: {command.args}")
    
    # Ensure user exists in DB
    await db.ensure_user(user_id)
    
    # Any deep link goes directly to rules/agreement
    await message.answer(
        texts.WELCOME_RULES,
        reply_markup=keyboards.agree_keyboard(),
        parse_mode="Markdown"
    )


@router.message(CommandStart())
async def start_normal(message: Message, db: Database) -> None:
    """Handle normal /start without deep link."""
    user_id = message.from_user.id
    logger.info(f"User {user_id} started normally")
    
    # Ensure user exists in DB
    await db.ensure_user(user_id)
    
    # Show welcome with Join button
    await message.answer(
        texts.WELCOME_START,
        reply_markup=keyboards.join_keyboard(),
        parse_mode="Markdown"
    )

