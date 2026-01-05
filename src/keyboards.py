"""
Inline keyboard builders for the Gatekeeper bot.
"""
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src import texts
from src.texts import get_text


def language_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for language selection."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=texts.BTN_LANG_EN, callback_data="lang:en"),
            InlineKeyboardButton(text=texts.BTN_LANG_RU, callback_data="lang:ru"),
        ]
    ])


def join_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard for initial /start (after language selected)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(texts.BTN_JOIN, lang), callback_data="lobby:join")]
    ])


def agree_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard for rules agreement."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(texts.BTN_AGREE, lang), callback_data="lobby:agree"),
            InlineKeyboardButton(text=get_text(texts.BTN_CANCEL, lang), callback_data="lobby:cancel"),
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


def try_again_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard shown after wrong captcha answer."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(texts.BTN_TRY_AGAIN, lang), callback_data="lobby:join")]
    ])


def cooldown_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard shown during cooldown."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(texts.BTN_TRY_LATER, lang), callback_data="lobby:check_cooldown")]
    ])
