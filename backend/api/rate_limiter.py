import asyncio
import time
from typing import Dict, Optional
from collections import deque
import structlog

logger = structlog.get_logger()


class TokenBucket:
    """
    Token Bucket Algorithm for rate limiting

    This implements a classic token bucket that:
    - Refills at a constant rate
    - Allows burst capacity
    - Blocks when tokens depleted
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket

        Args:
            capacity: Maximum number of tokens (burst capacity)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from bucket

        Args:
            tokens: Number of tokens to acquire

        Returns:
            bool: True if acquired successfully
        """
        async with self._lock:
            await self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            # Calculate wait time if no tokens available
            wait_time = (tokens - self.tokens) / self.refill_rate
            logger.info(
                "rate_limit_wait",
                tokens_needed=tokens,
                tokens_available=self.tokens,
                wait_seconds=wait_time,
            )

            await asyncio.sleep(wait_time)
            await self._refill()
            self.tokens -= tokens
            return True

    async def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_available_tokens(self) -> float:
        """Get current number of available tokens"""
        return self.tokens


class PriorityQueue:
    """Priority queue for API requests"""

    def __init__(self):
        self.queues = {
            "critical": deque(),  # Live price updates
            "high": deque(),  # User-initiated requests
            "medium": deque(),  # Background updates
            "low": deque(),  # Historical data, analytics
        }

    def add(self, priority: str, request):
        """Add request to priority queue"""
        if priority not in self.queues:
            priority = "medium"
        self.queues[priority].append(request)

    def get_next(self):
        """Get next request based on priority"""
        for priority in ["critical", "high", "medium", "low"]:
            if self.queues[priority]:
                return self.queues[priority].popleft()
        return None

    def size(self) -> int:
        """Get total queue size"""
        return sum(len(q) for q in self.queues.values())


class RateLimiter:
    """
    Multi-source rate limiter

    Manages rate limits for multiple APIs:
    - CoinGecko: 50 calls/minute (CRITICAL!)
    - Binance: 1200 calls/minute
    - Glassnode: 100 calls/day
    """

    def __init__(self):
        self.limiters: Dict[str, TokenBucket] = {}
        self.request_queues: Dict[str, PriorityQueue] = {}
        self.stats: Dict[str, Dict] = {}

        # Initialize limiters
        self._init_limiters()

    def _init_limiters(self):
        """Initialize rate limiters for each source"""

        # CoinGecko: 50 calls/minute = 0.833 calls/second
        # STRICT LIMIT - add safety margin (45/min = 0.75/s)
        self.limiters["coingecko"] = TokenBucket(capacity=45, refill_rate=0.75)

        # Binance: 1200 calls/minute = 20 calls/second
        # Add safety margin (1100/min = 18.33/s)
        self.limiters["binance"] = TokenBucket(capacity=1100, refill_rate=18.33)

        # Glassnode: 100 calls/day = 0.00115 calls/second
        self.limiters["glassnode"] = TokenBucket(capacity=100, refill_rate=0.00115)

        # CryptoQuant: Assume 300 calls/day
        self.limiters["cryptoquant"] = TokenBucket(capacity=300, refill_rate=0.00347)

        # Initialize queues and stats
        for source in self.limiters.keys():
            self.request_queues[source] = PriorityQueue()
            self.stats[source] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_wait_time": 0,
            }

        logger.info("rate_limiters_initialized", sources=list(self.limiters.keys()))

    async def acquire(
        self, source: str, priority: str = "medium", tokens: int = 1
    ) -> bool:
        """
        Acquire tokens for API request

        Args:
            source: API source name
            priority: Request priority (critical, high, medium, low)
            tokens: Number of tokens to acquire (default 1)

        Returns:
            bool: True if acquired successfully
        """
        if source not in self.limiters:
            logger.warning("rate_limiter_unknown_source", source=source)
            return True  # Allow if source not configured

        start_time = time.time()

        # Acquire token from bucket
        success = await self.limiters[source].acquire(tokens)

        wait_time = time.time() - start_time

        # Update stats
        self.stats[source]["total_requests"] += 1
        if success:
            self.stats[source]["successful_requests"] += 1
        else:
            self.stats[source]["failed_requests"] += 1
        self.stats[source]["total_wait_time"] += wait_time

        if wait_time > 0.1:  # Log significant waits
            logger.info(
                "rate_limit_acquired",
                source=source,
                priority=priority,
                wait_time=round(wait_time, 2),
                tokens_remaining=round(self.limiters[source].get_available_tokens(), 2),
            )

        return success

    def get_status(self) -> Dict[str, Dict]:
        """Get current rate limiter status"""
        status = {}

        for source, limiter in self.limiters.items():
            available_tokens = limiter.get_available_tokens()
            capacity = limiter.capacity
            usage_pct = ((capacity - available_tokens) / capacity) * 100

            status[source] = {
                "available_tokens": round(available_tokens, 2),
                "capacity": capacity,
                "usage_percent": round(usage_pct, 2),
                "refill_rate": limiter.refill_rate,
                "stats": self.stats[source],
            }

        return status

    def reset_stats(self, source: Optional[str] = None):
        """Reset statistics"""
        if source:
            if source in self.stats:
                self.stats[source] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "total_wait_time": 0,
                }
        else:
            for source in self.stats:
                self.reset_stats(source)


# Global rate limiter instance
rate_limiter = RateLimiter()
