"""
Inline keyboard builders for the Gatekeeper bot.
"""
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src import texts


def join_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for initial /start (no deep link)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_JOIN, callback_data="lobby:join")]
    ])


def agree_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for rules agreement."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=texts.BTN_AGREE, callback_data="lobby:agree"),
            InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="lobby:cancel"),
        ]
    ])


def captcha_keyboard(correct_emoji: str) -> InlineKeyboardMarkup:
    """
    Generate captcha keyboard with 4 emoji buttons.
    One is correct, three are random decoys.
    """
    # Pick 3 random decoys that aren't the correct answer
    decoys = [e for e in texts.CAPTCHA_DECOYS if e != correct_emoji]
    selected_decoys = random.sample(decoys, 3)
    
    # Combine and shuffle
    options = [correct_emoji] + selected_decoys
    random.shuffle(options)
    
    # Create buttons in a single row
    buttons = [
        InlineKeyboardButton(
            text=emoji,
            callback_data=f"captcha:{emoji}"
        )
        for emoji in options
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def try_again_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown after wrong captcha answer."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_TRY_AGAIN, callback_data="lobby:join")]
    ])


def cooldown_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown during cooldown."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_TRY_LATER, callback_data="lobby:check_cooldown")]
    ])

