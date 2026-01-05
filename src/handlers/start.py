"""
Handler for /start command and deep links.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject

from src import texts, keyboards
from src.texts import get_text
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
    
    # Check if user has selected a language
    lang = await db.get_language(user_id)
    
    if not lang:
        # Show language selection first
        await message.answer(
            texts.LANGUAGE_SELECT,
            reply_markup=keyboards.language_keyboard(),
            parse_mode="Markdown"
        )
    else:
        # Language already selected, go to rules
        await message.answer(
            get_text(texts.WELCOME_RULES, lang),
            reply_markup=keyboards.agree_keyboard(lang),
            parse_mode="Markdown"
        )


@router.message(CommandStart())
async def start_normal(message: Message, db: Database) -> None:
    """Handle normal /start without deep link."""
    user_id = message.from_user.id
    logger.info(f"User {user_id} started normally")
    
    # Ensure user exists in DB
    await db.ensure_user(user_id)
    
    # Check if user has selected a language
    lang = await db.get_language(user_id)
    
    if not lang:
        # Show language selection first
        await message.answer(
            texts.LANGUAGE_SELECT,
            reply_markup=keyboards.language_keyboard(),
            parse_mode="Markdown"
        )
    else:
        # Language already selected, show welcome
        await message.answer(
            get_text(texts.WELCOME_START, lang),
            reply_markup=keyboards.join_keyboard(lang),
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("lang:"))
async def on_language_select(callback: CallbackQuery, db: Database) -> None:
    """Handle language selection."""
    user_id = callback.from_user.id
    lang = callback.data.split(":", 1)[1]  # "en" or "ru"
    
    logger.info(f"User {user_id} selected language: {lang}")
    
    # Save language preference
    await db.set_language(user_id, lang)
    
    # Show welcome message in selected language
    await callback.message.edit_text(
        get_text(texts.WELCOME_START, lang),
        reply_markup=keyboards.join_keyboard(lang),
        parse_mode="Markdown"
    )
    await callback.answer()
