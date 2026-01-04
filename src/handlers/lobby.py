"""
Handlers for lobby flow: agreement, captcha, callbacks.
"""
import time
import random
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src import texts, keyboards
from src.db import Database
from src.config import Config

logger = logging.getLogger(__name__)
router = Router(name="lobby")

# Rate limiting: track last callback time per user
_last_callback: dict[int, float] = {}
CALLBACK_COOLDOWN = 0.3  # 300ms between callbacks


def _check_rate_limit(user_id: int) -> bool:
    """Check if user is spamming callbacks. Returns True if allowed."""
    now = time.time()
    last = _last_callback.get(user_id, 0)
    if now - last < CALLBACK_COOLDOWN:
        return False
    _last_callback[user_id] = now
    return True


# Store active captcha challenges per user (in memory, resets on restart)
_active_challenges: dict[int, str] = {}


def _get_random_challenge() -> tuple[str, str, str]:
    """Get a random captcha challenge. Returns (en_text, ru_text, correct_emoji)."""
    return random.choice(texts.CAPTCHA_CHALLENGES)


@router.callback_query(F.data == "lobby:join")
async def on_join(callback: CallbackQuery, db: Database) -> None:
    """User taps Join button - show rules."""
    user_id = callback.from_user.id
    
    if not _check_rate_limit(user_id):
        await callback.answer()
        return
    
    logger.info(f"User {user_id} tapped Join")
    
    # Check if in cooldown first
    in_cooldown, remaining = await db.is_in_cooldown(user_id)
    if in_cooldown:
        minutes = (remaining // 60) + 1
        await callback.message.edit_text(
            texts.CAPTCHA_COOLDOWN.format(minutes=minutes),
            reply_markup=keyboards.cooldown_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        texts.WELCOME_RULES,
        reply_markup=keyboards.agree_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "lobby:agree")
async def on_agree(callback: CallbackQuery, db: Database) -> None:
    """User agrees to rules - show captcha."""
    user_id = callback.from_user.id
    
    if not _check_rate_limit(user_id):
        await callback.answer()
        return
    
    logger.info(f"User {user_id} agreed to rules")
    
    # Check cooldown
    in_cooldown, remaining = await db.is_in_cooldown(user_id)
    if in_cooldown:
        minutes = (remaining // 60) + 1
        await callback.message.edit_text(
            texts.CAPTCHA_COOLDOWN.format(minutes=minutes),
            reply_markup=keyboards.cooldown_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Mark agreed
    await db.set_agreed(user_id)
    
    # Generate captcha challenge
    challenge_en, challenge_ru, correct_emoji = _get_random_challenge()
    _active_challenges[user_id] = correct_emoji
    
    await callback.message.edit_text(
        texts.CAPTCHA_INTRO.format(challenge_en=challenge_en, challenge_ru=challenge_ru),
        reply_markup=keyboards.captcha_keyboard(correct_emoji),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "lobby:cancel")
async def on_cancel(callback: CallbackQuery) -> None:
    """User cancels - show cancelled message."""
    user_id = callback.from_user.id
    
    if not _check_rate_limit(user_id):
        await callback.answer()
        return
    
    logger.info(f"User {user_id} cancelled")
    
    # Clear any active challenge
    _active_challenges.pop(user_id, None)
    
    await callback.message.edit_text(
        texts.CANCELLED,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("captcha:"))
async def on_captcha_answer(callback: CallbackQuery, db: Database, config: Config) -> None:
    """User picks a captcha answer."""
    user_id = callback.from_user.id
    
    if not _check_rate_limit(user_id):
        await callback.answer()
        return
    
    selected_emoji = callback.data.split(":", 1)[1]
    correct_emoji = _active_challenges.get(user_id)
    
    logger.info(f"User {user_id} selected {selected_emoji}, correct is {correct_emoji}")
    
    # Check cooldown first
    in_cooldown, remaining = await db.is_in_cooldown(user_id)
    if in_cooldown:
        minutes = (remaining // 60) + 1
        await callback.message.edit_text(
            texts.CAPTCHA_COOLDOWN.format(minutes=minutes),
            reply_markup=keyboards.cooldown_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # No active challenge (maybe bot restarted)
    if not correct_emoji:
        # Regenerate captcha
        challenge_en, challenge_ru, correct_emoji = _get_random_challenge()
        _active_challenges[user_id] = correct_emoji
        await callback.message.edit_text(
            texts.CAPTCHA_INTRO.format(challenge_en=challenge_en, challenge_ru=challenge_ru),
            reply_markup=keyboards.captcha_keyboard(correct_emoji),
            parse_mode="Markdown"
        )
        await callback.answer("Session expired, please try again.")
        return
    
    if selected_emoji == correct_emoji:
        # Success!
        logger.info(f"User {user_id} passed captcha")
        _active_challenges.pop(user_id, None)
        await db.set_verified(user_id)
        
        await callback.message.edit_text(
            texts.CAPTCHA_SUCCESS.format(invite_link=config.join_request_invite_link),
            parse_mode="Markdown"
        )
        await callback.answer("✅ Correct!")
    else:
        # Wrong answer
        count, cooldown_until = await db.increment_attempts(
            user_id, config.max_attempts, config.cooldown_seconds
        )
        
        if cooldown_until:
            # Entered cooldown
            logger.info(f"User {user_id} entered cooldown until {cooldown_until}")
            _active_challenges.pop(user_id, None)
            minutes = (config.cooldown_seconds // 60)
            await callback.message.edit_text(
                texts.CAPTCHA_COOLDOWN.format(minutes=minutes),
                reply_markup=keyboards.cooldown_keyboard(),
                parse_mode="Markdown"
            )
            await callback.answer("❌ Too many attempts!")
        else:
            # Can try again
            remaining = config.max_attempts - count
            logger.info(f"User {user_id} wrong answer, {remaining} attempts left")
            
            # Generate new challenge
            challenge_en, challenge_ru, correct_emoji = _get_random_challenge()
            _active_challenges[user_id] = correct_emoji
            
            await callback.message.edit_text(
                texts.CAPTCHA_WRONG.format(remaining=remaining) + "\n\n" + 
                texts.CAPTCHA_INTRO.format(challenge_en=challenge_en, challenge_ru=challenge_ru),
                reply_markup=keyboards.captcha_keyboard(correct_emoji),
                parse_mode="Markdown"
            )
            await callback.answer("❌ Wrong!")


@router.callback_query(F.data == "lobby:check_cooldown")
async def on_check_cooldown(callback: CallbackQuery, db: Database) -> None:
    """User checks if cooldown is over."""
    user_id = callback.from_user.id
    
    if not _check_rate_limit(user_id):
        await callback.answer()
        return
    
    in_cooldown, remaining = await db.is_in_cooldown(user_id)
    
    if in_cooldown:
        minutes = (remaining // 60) + 1
        await callback.answer(f"Please wait {minutes} more minute(s)")
    else:
        # Cooldown over, show rules again
        logger.info(f"User {user_id} cooldown expired")
        await callback.message.edit_text(
            texts.WELCOME_RULES,
            reply_markup=keyboards.agree_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer("You can try again now!")
