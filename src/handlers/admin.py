"""
Admin command handlers (DM only).
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from src import texts
from src.db import Database
from src.config import Config

logger = logging.getLogger(__name__)
router = Router(name="admin")


async def is_admin(message: Message, config: Config) -> bool:
    """
    Check if user is authorized as admin.
    Uses ADMIN_IDS env var as fallback.
    Could be enhanced to use getChatAdministrators API.
    """
    user_id = message.from_user.id
    
    # Check env var admin list
    if user_id in config.admin_ids:
        return True
    
    # Enhancement: Could check getChatAdministrators here
    # For v0, we rely on ADMIN_IDS
    
    return False


@router.message(Command("lockdown"))
async def cmd_lockdown(message: Message, db: Database, config: Config) -> None:
    """Toggle lockdown mode: /lockdown on|off"""
    if not await is_admin(message, config):
        await message.answer(texts.ADMIN_NOT_AUTHORIZED)
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Usage: /lockdown on|off")
        return
    
    mode = args[1].lower().strip()
    
    if mode == "on":
        await db.set_lockdown(True)
        logger.info(f"Admin {message.from_user.id} enabled lockdown")
        await message.answer(texts.ADMIN_LOCKDOWN_ON)
    elif mode == "off":
        await db.set_lockdown(False)
        logger.info(f"Admin {message.from_user.id} disabled lockdown")
        await message.answer(texts.ADMIN_LOCKDOWN_OFF)
    else:
        await message.answer("Usage: /lockdown on|off")


@router.message(Command("mode"))
async def cmd_mode(message: Message, db: Database, config: Config) -> None:
    """Toggle strict/soft mode: /mode soft|strict"""
    if not await is_admin(message, config):
        await message.answer(texts.ADMIN_NOT_AUTHORIZED)
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Usage: /mode soft|strict")
        return
    
    mode = args[1].lower().strip()
    
    if mode == "strict":
        await db.set_strict_mode(True)
        logger.info(f"Admin {message.from_user.id} enabled strict mode")
        await message.answer(texts.ADMIN_MODE_STRICT)
    elif mode == "soft":
        await db.set_strict_mode(False)
        logger.info(f"Admin {message.from_user.id} enabled soft mode")
        await message.answer(texts.ADMIN_MODE_SOFT)
    else:
        await message.answer("Usage: /mode soft|strict")


@router.message(Command("status"))
async def cmd_status(message: Message, db: Database, config: Config) -> None:
    """Show current bot status and stats."""
    if not await is_admin(message, config):
        await message.answer(texts.ADMIN_NOT_AUTHORIZED)
        return
    
    lockdown = await db.get_lockdown()
    strict_mode = await db.get_strict_mode(config.strict_mode)
    verified_24h = await db.count_verified_last_24h()
    total_users = await db.count_total_users()
    
    mode_str = "Strict" if strict_mode else "Soft"
    lockdown_str = "🔒 ON" if lockdown else "🔓 OFF"
    
    await message.answer(
        texts.ADMIN_STATUS.format(
            mode=mode_str,
            lockdown=lockdown_str,
            verified_24h=verified_24h,
            total_users=total_users
        ),
        parse_mode="Markdown"
    )


@router.message(Command("adminhelp"))
async def cmd_admin_help(message: Message, config: Config) -> None:
    """Show admin commands help."""
    if not await is_admin(message, config):
        await message.answer(texts.ADMIN_NOT_AUTHORIZED)
        return
    
    await message.answer(texts.ADMIN_HELP, parse_mode="Markdown")

