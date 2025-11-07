"""
Redis caching and memory management
"""
import redis
import json
import os
from typing import Any, Optional, Callable
from datetime import timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,  # Auto-decode to strings
        max_connections=50,
        socket_timeout=5,
        socket_connect_timeout=5,
    )
    # Test connection
    redis_client.ping()
    logger.info(f"✅ Redis connected: {REDIS_URL}")
except redis.ConnectionError as e:
    logger.warning(f"⚠️  Redis connection failed: {e}. Caching disabled.")
    redis_client = None


class Cache:
    """Redis cache manager"""

    # TTL constants (in seconds)
    TTL_SESSION = 30 * 24 * 60 * 60  # 30 days
    TTL_MEMBER = 60 * 60  # 1 hour
    TTL_MESSAGE = 15 * 60  # 15 minutes
    TTL_AVATAR = 24 * 60 * 60  # 24 hours
    TTL_RATE_LIMIT = 60  # 1 minute

    @staticmethod
    def _make_key(*parts) -> str:
        """Generate cache key"""
        return ":".join(str(p) for p in parts)

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        if not redis_client:
            return None

        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        if not redis_client:
            return False

        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)  # default=str for datetime
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    @staticmethod
    def delete(key: str):
        """Delete key from cache"""
        if not redis_client:
            return False

        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    @staticmethod
    def delete_pattern(pattern: str):
        """Delete all keys matching pattern"""
        if not redis_client:
            return 0

        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0

    @staticmethod
    def increment(key: str, amount: int = 1, ttl: int = 60) -> int:
        """Increment counter (for rate limiting)"""
        if not redis_client:
            return amount

        try:
            pipe = redis_client.pipeline()
            pipe.incr(key, amount)
            pipe.expire(key, ttl)
            results = pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return amount

    # User session caching
    @staticmethod
    def get_session(user_id: int) -> Optional[dict]:
        """Get user session"""
        key = Cache._make_key("session", user_id)
        return Cache.get(key)

    @staticmethod
    def set_session(user_id: int, session_data: dict):
        """Cache user session"""
        key = Cache._make_key("session", user_id)
        Cache.set(key, session_data, Cache.TTL_SESSION)

    @staticmethod
    def delete_session(user_id: int):
        """Delete user session"""
        key = Cache._make_key("session", user_id)
        Cache.delete(key)

    # Member caching
    @staticmethod
    def get_members(user_id: int) -> Optional[list]:
        """Get cached members for user"""
        key = Cache._make_key("members", user_id)
        return Cache.get(key)

    @staticmethod
    def set_members(user_id: int, members: list):
        """Cache user's members"""
        key = Cache._make_key("members", user_id)
        Cache.set(key, members, Cache.TTL_MEMBER)

    @staticmethod
    def invalidate_members(user_id: int):
        """Invalidate member cache"""
        key = Cache._make_key("members", user_id)
        Cache.delete(key)

    # Message caching
    @staticmethod
    def get_recent_messages(limit: int = 50) -> Optional[list]:
        """Get cached recent messages"""
        key = Cache._make_key("messages", "recent", limit)
        return Cache.get(key)

    @staticmethod
    def set_recent_messages(messages: list, limit: int = 50):
        """Cache recent messages"""
        key = Cache._make_key("messages", "recent", limit)
        Cache.set(key, messages, Cache.TTL_MESSAGE)

    @staticmethod
    def invalidate_messages():
        """Invalidate message cache"""
        Cache.delete_pattern("messages:*")

    # Rate limiting
    @staticmethod
    def check_rate_limit(key: str, limit: int, window: int = 60) -> tuple[bool, int]:
        """
        Check rate limit for a key
        Returns (is_allowed, current_count)
        """
        count = Cache.increment(key, 1, window)
        return (count <= limit, count)

    @staticmethod
    def get_rate_limit(key: str) -> int:
        """Get current rate limit count"""
        if not redis_client:
            return 0
        try:
            value = redis_client.get(key)
            return int(value) if value else 0
        except:
            return 0

    # Statistics
    @staticmethod
    def get_stats() -> dict:
        """Get cache statistics"""
        if not redis_client:
            return {
                "status": "disabled",
                "message": "Redis is not available"
            }

        try:
            info = redis_client.info()
            return {
                "status": "connected",
                "memory_used": info["used_memory_human"],
                "memory_peak": info["used_memory_peak_human"],
                "keys": redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) /
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1))
                    * 100
                ),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Cache decorator
def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results

    Usage:
        @cached(ttl=3600, key_prefix="user")
        def get_user(user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = Cache._make_key(
                key_prefix or func.__name__,
                *args,
                *[f"{k}={v}" for k, v in sorted(kwargs.items())]
            )

            # Try cache first
            cached_result = Cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result

            # Cache miss - execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)

            # Cache result
            Cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


# Rate limit decorator
def rate_limit(limit: int, window: int = 60, key_func: Optional[Callable] = None):
    """
    Decorator for rate limiting

    Usage:
        @rate_limit(limit=5, window=60)
        def login(username: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"rate_limit:{func.__name__}"

            # Check rate limit
            is_allowed, count = Cache.check_rate_limit(key, limit, window)

            if not is_allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {window} seconds."
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator
