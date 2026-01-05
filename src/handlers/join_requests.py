"""
Handler for chat join requests - auto-approval logic.
"""
import logging
from aiogram import Router, F
from aiogram.types import ChatJoinRequest

from src import texts
from src.texts import get_text
from src.db import Database
from src.config import Config

logger = logging.getLogger(__name__)
router = Router(name="join_requests")


@router.chat_join_request()
async def on_join_request(request: ChatJoinRequest, db: Database, config: Config) -> None:
    """
    Handle join request to the target supergroup.
    Auto-approve if user verified recently, otherwise leave for manual approval.
    """
    user_id = request.from_user.id
    chat_id = request.chat.id
    
    # Only handle requests for our target group
    if chat_id != config.group_chat_id:
        logger.debug(f"Ignoring join request for chat {chat_id} (not target group)")
        return
    
    logger.info(f"Join request from user {user_id} for group {chat_id}")
    
    # Record the join request time
    await db.set_join_request_time(user_id)
    
    # Get user's language (default to English if not set)
    lang = await db.get_language(user_id) or "en"
    
    # Check lockdown mode
    lockdown = await db.get_lockdown()
    if lockdown:
        logger.info(f"Lockdown active, declining user {user_id}")
        try:
            await request.decline()
            await request.bot.send_message(
                user_id,
                get_text(texts.DECLINED_VERIFY_FIRST, lang),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"Failed to decline/DM user {user_id}: {e}")
        return
    
    # Check if user is verified recently
    verified_recently = await db.is_verified_recently(user_id, config.verify_ttl_seconds)
    
    # Check if in cooldown (shouldn't approve during cooldown)
    in_cooldown, _ = await db.is_in_cooldown(user_id)
    
    if verified_recently and not in_cooldown:
        # Auto-approve!
        logger.info(f"Auto-approving user {user_id}")
        try:
            await request.approve()
            # DM welcome message
            await request.bot.send_message(
                user_id,
                get_text(texts.APPROVED, lang),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to approve/DM user {user_id}: {e}")
    else:
        # Check strict mode
        strict_mode = await db.get_strict_mode(config.strict_mode)
        
        if strict_mode:
            # Decline and ask to verify first
            logger.info(f"Strict mode: declining unverified user {user_id}")
            try:
                await request.decline()
                await request.bot.send_message(
                    user_id,
                    get_text(texts.DECLINED_VERIFY_FIRST, lang),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.warning(f"Failed to decline/DM user {user_id}: {e}")
        else:
            # Soft mode: leave pending for manual approval
            logger.info(f"Soft mode: leaving user {user_id} pending for manual approval")
            # Don't do anything - request stays pending
