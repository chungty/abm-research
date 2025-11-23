"""
Rate limiting utilities for API calls and web scraping
"""
import asyncio
from typing import Optional
from datetime import datetime, timedelta


class RateLimiter:
    """Async rate limiter to prevent overwhelming APIs and websites"""

    def __init__(self, delay: float = 1.0, burst_limit: int = 5):
        """
        Initialize rate limiter

        Args:
            delay: Minimum seconds between requests
            burst_limit: Maximum concurrent requests before throttling
        """
        self.delay = delay
        self.burst_limit = burst_limit
        self.last_request_time: Optional[datetime] = None
        self.active_requests = 0
        self._semaphore = asyncio.Semaphore(burst_limit)

    async def __aenter__(self):
        """Async context manager entry - enforce rate limit"""
        await self._semaphore.acquire()
        self.active_requests += 1

        # Enforce minimum delay between requests
        if self.last_request_time:
            time_since_last = (datetime.now() - self.last_request_time).total_seconds()
            if time_since_last < self.delay:
                await asyncio.sleep(self.delay - time_since_last)

        self.last_request_time = datetime.now()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - release semaphore"""
        self.active_requests -= 1
        self._semaphore.release()

    async def wait(self):
        """Explicitly wait for rate limit (alternative to context manager)"""
        async with self:
            pass

    def get_stats(self) -> dict:
        """Get current rate limiter statistics"""
        return {
            'delay': self.delay,
            'burst_limit': self.burst_limit,
            'active_requests': self.active_requests,
            'available_slots': self.burst_limit - self.active_requests,
            'last_request_time': self.last_request_time.isoformat() if self.last_request_time else None
        }