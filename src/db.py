"""
Database module - SQLite persistence using aiosqlite.
"""
import time
import aiosqlite
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UserState:
    """User state from database."""
    user_id: int
    agreed_at: int | None
    verified_at: int | None
    attempts_count: int
    attempts_window_start: int | None
    cooldown_until: int | None
    last_join_request_at: int | None


class Database:
    """Async SQLite database wrapper."""
    
    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection | None = None
    
    async def connect(self) -> None:
        """Initialize database connection and create tables."""
        # Ensure directory exists
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        
        # Create tables
        await self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                agreed_at INTEGER NULL,
                verified_at INTEGER NULL,
                attempts_count INTEGER NOT NULL DEFAULT 0,
                attempts_window_start INTEGER NULL,
                cooldown_until INTEGER NULL,
                last_join_request_at INTEGER NULL
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        await self._conn.commit()
    
    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
    
    # --- User operations ---
    
    async def get_user(self, user_id: int) -> UserState | None:
        """Get user state by ID."""
        async with self._conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return UserState(
                    user_id=row["user_id"],
                    agreed_at=row["agreed_at"],
                    verified_at=row["verified_at"],
                    attempts_count=row["attempts_count"],
                    attempts_window_start=row["attempts_window_start"],
                    cooldown_until=row["cooldown_until"],
                    last_join_request_at=row["last_join_request_at"],
                )
            return None
    
    async def ensure_user(self, user_id: int) -> UserState:
        """Get user state, creating if doesn't exist."""
        # Use INSERT OR IGNORE to handle race conditions
        await self._conn.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
        )
        await self._conn.commit()
        
        # Now fetch the user (guaranteed to exist)
        user = await self.get_user(user_id)
        return user
    
    async def set_agreed(self, user_id: int) -> None:
        """Mark user as agreed to rules."""
        now = int(time.time())
        await self._conn.execute(
            """INSERT INTO users (user_id, agreed_at) VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET agreed_at = ?""",
            (user_id, now, now)
        )
        await self._conn.commit()
    
    async def set_verified(self, user_id: int) -> None:
        """Mark user as verified (passed captcha)."""
        now = int(time.time())
        await self._conn.execute(
            """UPDATE users SET 
               verified_at = ?,
               attempts_count = 0,
               attempts_window_start = NULL,
               cooldown_until = NULL
               WHERE user_id = ?""",
            (now, user_id)
        )
        await self._conn.commit()
    
    async def increment_attempts(self, user_id: int, max_attempts: int, cooldown_seconds: int) -> tuple[int, int | None]:
        """
        Increment failed attempts. Returns (new_count, cooldown_until if triggered).
        Resets window if > 10 minutes since last attempt.
        """
        now = int(time.time())
        user = await self.ensure_user(user_id)
        
        # Reset window if stale (> 10 min since window start)
        window_start = user.attempts_window_start
        if window_start and (now - window_start) > 600:
            window_start = None
        
        if window_start is None:
            window_start = now
            count = 1
        else:
            count = user.attempts_count + 1
        
        cooldown_until = None
        if count >= max_attempts:
            cooldown_until = now + cooldown_seconds
        
        await self._conn.execute(
            """UPDATE users SET 
               attempts_count = ?,
               attempts_window_start = ?,
               cooldown_until = ?
               WHERE user_id = ?""",
            (count, window_start, cooldown_until, user_id)
        )
        await self._conn.commit()
        
        return count, cooldown_until
    
    async def reset_attempts(self, user_id: int) -> None:
        """Reset attempt counter (after successful captcha or cooldown)."""
        await self._conn.execute(
            """UPDATE users SET 
               attempts_count = 0,
               attempts_window_start = NULL,
               cooldown_until = NULL
               WHERE user_id = ?""",
            (user_id,)
        )
        await self._conn.commit()
    
    async def set_join_request_time(self, user_id: int) -> None:
        """Record when user made a join request."""
        now = int(time.time())
        await self._conn.execute(
            """INSERT INTO users (user_id, last_join_request_at) VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET last_join_request_at = ?""",
            (user_id, now, now)
        )
        await self._conn.commit()
    
    async def is_verified_recently(self, user_id: int, ttl_seconds: int) -> bool:
        """Check if user was verified within TTL."""
        user = await self.get_user(user_id)
        if not user or not user.verified_at:
            return False
        
        now = int(time.time())
        return (now - user.verified_at) <= ttl_seconds
    
    async def is_in_cooldown(self, user_id: int) -> tuple[bool, int]:
        """Check if user is in cooldown. Returns (is_cooldown, seconds_remaining)."""
        user = await self.get_user(user_id)
        if not user or not user.cooldown_until:
            return False, 0
        
        now = int(time.time())
        if now >= user.cooldown_until:
            # Cooldown expired, reset
            await self.reset_attempts(user_id)
            return False, 0
        
        return True, user.cooldown_until - now
    
    # --- Settings operations ---
    
    async def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting value."""
        async with self._conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["value"] if row else default
    
    async def set_setting(self, key: str, value: str) -> None:
        """Set a setting value."""
        await self._conn.execute(
            """INSERT INTO settings (key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value = ?""",
            (key, value, value)
        )
        await self._conn.commit()
    
    async def get_lockdown(self) -> bool:
        """Get lockdown mode status."""
        val = await self.get_setting("lockdown", "0")
        return val == "1"
    
    async def set_lockdown(self, enabled: bool) -> None:
        """Set lockdown mode."""
        await self.set_setting("lockdown", "1" if enabled else "0")
    
    async def get_strict_mode(self, default: bool = False) -> bool:
        """Get strict mode status."""
        val = await self.get_setting("strict_mode")
        if not val:
            return default
        return val == "1"
    
    async def set_strict_mode(self, enabled: bool) -> None:
        """Set strict mode."""
        await self.set_setting("strict_mode", "1" if enabled else "0")
    
    # --- Stats ---
    
    async def count_verified_last_24h(self) -> int:
        """Count users verified in last 24 hours."""
        cutoff = int(time.time()) - 86400
        async with self._conn.execute(
            "SELECT COUNT(*) as cnt FROM users WHERE verified_at > ?", (cutoff,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["cnt"] if row else 0
    
    async def count_total_users(self) -> int:
        """Count total users in database."""
        async with self._conn.execute("SELECT COUNT(*) as cnt FROM users") as cursor:
            row = await cursor.fetchone()
            return row["cnt"] if row else 0

