"""
Configuration module - loads settings from environment variables.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_bool(key: str, default: bool = False) -> bool:
    """Parse boolean from env var (accepts true/false/1/0)."""
    val = os.getenv(key, str(default)).lower()
    return val in ("true", "1", "yes")


def _get_int(key: str, default: int) -> int:
    """Parse integer from env var."""
    return int(os.getenv(key, str(default)))


def _get_int_list(key: str) -> list[int]:
    """Parse comma-separated list of integers."""
    val = os.getenv(key, "")
    if not val.strip():
        return []
    return [int(x.strip()) for x in val.split(",") if x.strip()]


@dataclass(frozen=True)
class Config:
    """Immutable configuration loaded at startup."""
    
    # Required
    bot_token: str
    group_chat_id: int
    join_request_invite_link: str
    
    # Timing
    verify_ttl_seconds: int
    cooldown_seconds: int
    max_attempts: int
    
    # Modes (can be overridden by DB)
    strict_mode: bool
    lockdown: bool
    
    # Storage
    sqlite_path: str
    
    # Admin IDs fallback
    admin_ids: list[int]


def load_config() -> Config:
    """Load and validate configuration from environment."""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required")
    
    group_chat_id = os.getenv("GROUP_CHAT_ID")
    if not group_chat_id:
        raise ValueError("GROUP_CHAT_ID environment variable is required")
    
    invite_link = os.getenv("JOIN_REQUEST_INVITE_LINK")
    if not invite_link:
        raise ValueError("JOIN_REQUEST_INVITE_LINK environment variable is required")
    
    return Config(
        bot_token=bot_token,
        group_chat_id=int(group_chat_id),
        join_request_invite_link=invite_link,
        verify_ttl_seconds=_get_int("VERIFY_TTL_SECONDS", 300),
        cooldown_seconds=_get_int("COOLDOWN_SECONDS", 600),
        max_attempts=_get_int("MAX_ATTEMPTS", 3),
        strict_mode=_get_bool("STRICT_MODE", False),
        lockdown=_get_bool("LOCKDOWN", False),
        sqlite_path=os.getenv("SQLITE_PATH", "./data/gatekeeper.sqlite"),
        admin_ids=_get_int_list("ADMIN_IDS"),
    )



