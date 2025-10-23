import json
import asyncio
from typing import Optional, Any
from datetime import datetime, timedelta
import structlog

try:
    import redis.asyncio as redis
except ImportError:
    import redis

logger = structlog.get_logger()


class CacheManager:
    """
    Multi-level caching system

    L1: Redis (Memory) - Fast, volatile
    L2: In-memory dict (Fallback if Redis unavailable)

    Cache TTLs:
    - Live prices: 30 seconds
    - Technical indicators: 1 minute
    - Historical data: 1 hour
    - Market stats: 5 minutes
    - AI analyses: 10 minutes
    """

    # Default TTLs (seconds)
    TTL_PRICE = 30
    TTL_TECHNICAL = 60
    TTL_HISTORICAL = 3600
    TTL_MARKET_STATS = 300
    TTL_AI_ANALYSIS = 600

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize cache manager

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_cache: dict = {}  # In-memory fallback
        self.use_redis = True

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("redis_connected", url=self.redis_url)

        except Exception as e:
            logger.warning(
                "redis_connection_failed",
                error=str(e),
                fallback="using_in_memory_cache",
            )
            self.use_redis = False
            self.redis_client = None

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            if self.use_redis and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to in-memory cache
                cached = self.fallback_cache.get(key)
                if cached:
                    value, expires_at = cached
                    if datetime.utcnow() < expires_at:
                        return value
                    else:
                        # Expired
                        del self.fallback_cache[key]

            return None

        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int = TTL_MARKET_STATS):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        try:
            serialized = json.dumps(value, default=str)

            if self.use_redis and self.redis_client:
                await self.redis_client.setex(key, ttl, serialized)
            else:
                # Fallback to in-memory cache
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                self.fallback_cache[key] = (value, expires_at)

        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))

    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.delete(key)
            else:
                self.fallback_cache.pop(key, None)

        except Exception as e:
            logger.error("cache_delete_error", key=key, error=str(e))

    async def clear_pattern(self, pattern: str):
        """
        Clear all keys matching pattern

        Args:
            pattern: Key pattern (e.g., "coin:*")
        """
        try:
            if self.use_redis and self.redis_client:
                keys = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    keys.append(key)

                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info("cache_cleared", pattern=pattern, count=len(keys))
            else:
                # Clear from fallback cache
                keys_to_delete = [
                    k for k in self.fallback_cache.keys() if pattern.replace("*", "") in k
                ]
                for key in keys_to_delete:
                    del self.fallback_cache[key]

        except Exception as e:
            logger.error("cache_clear_pattern_error", pattern=pattern, error=str(e))

    async def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            if self.use_redis and self.redis_client:
                info = await self.redis_client.info("stats")
                return {
                    "type": "redis",
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                    "keys": await self.redis_client.dbsize(),
                }
            else:
                # Fallback cache stats
                active_keys = sum(
                    1
                    for _, expires_at in self.fallback_cache.values()
                    if datetime.utcnow() < expires_at
                )
                return {
                    "type": "in_memory",
                    "keys": active_keys,
                    "total_keys": len(self.fallback_cache),
                }

        except Exception as e:
            logger.error("cache_stats_error", error=str(e))
            return {"type": "error", "error": str(e)}

    # Helper methods for specific cache keys

    def _make_price_key(self, symbol: str) -> str:
        return f"price:{symbol}"

    def _make_technical_key(self, symbol: str) -> str:
        return f"technical:{symbol}"

    def _make_ai_analysis_key(self, symbol: str) -> str:
        return f"ai_analysis:{symbol}"

    def _make_signal_key(self, symbol: str) -> str:
        return f"signal:{symbol}"

    async def get_price(self, symbol: str) -> Optional[dict]:
        """Get cached price"""
        return await self.get(self._make_price_key(symbol))

    async def set_price(self, symbol: str, price_data: dict):
        """Cache price data"""
        await self.set(self._make_price_key(symbol), price_data, self.TTL_PRICE)

    async def get_technical(self, symbol: str) -> Optional[dict]:
        """Get cached technical indicators"""
        return await self.get(self._make_technical_key(symbol))

    async def set_technical(self, symbol: str, technical_data: dict):
        """Cache technical indicators"""
        await self.set(self._make_technical_key(symbol), technical_data, self.TTL_TECHNICAL)

    async def get_ai_analysis(self, symbol: str) -> Optional[dict]:
        """Get cached AI analysis"""
        return await self.get(self._make_ai_analysis_key(symbol))

    async def set_ai_analysis(self, symbol: str, analysis_data: dict):
        """Cache AI analysis"""
        await self.set(self._make_ai_analysis_key(symbol), analysis_data, self.TTL_AI_ANALYSIS)

    async def get_signal(self, symbol: str) -> Optional[dict]:
        """Get cached signal"""
        return await self.get(self._make_signal_key(symbol))

    async def set_signal(self, symbol: str, signal_data: dict):
        """Cache signal"""
        await self.set(self._make_signal_key(symbol), signal_data, self.TTL_TECHNICAL)


# Global cache manager instance
cache_manager = CacheManager()
