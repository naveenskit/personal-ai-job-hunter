import asyncio
from dataclasses import dataclass
from time import monotonic

from app.core.exceptions import RateLimitError


@dataclass(slots=True)
class TokenBucket:
    capacity: int
    refill_rate_per_second: float
    tokens: float
    updated_at: float

    @classmethod
    def per_minute(cls, limit: int) -> "TokenBucket":
        return cls(
            capacity=limit,
            refill_rate_per_second=limit / 60,
            tokens=float(limit),
            updated_at=monotonic(),
        )

    def refill(self) -> None:
        now = monotonic()
        elapsed = now - self.updated_at
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate_per_second)
        self.updated_at = now


class AsyncRateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        if limit_per_minute <= 0:
            raise ValueError("limit_per_minute must be greater than zero")
        self._bucket = TokenBucket.per_minute(limit_per_minute)
        self._lock = asyncio.Lock()

    async def acquire(self, *, wait: bool = True) -> None:
        while True:
            async with self._lock:
                self._bucket.refill()
                if self._bucket.tokens >= 1:
                    self._bucket.tokens -= 1
                    return

                if not wait:
                    raise RateLimitError("Rate limit exceeded")

                missing = 1 - self._bucket.tokens
                delay = missing / self._bucket.refill_rate_per_second

            await asyncio.sleep(max(delay, 0.01))

    async def __aenter__(self) -> "AsyncRateLimiter":
        await self.acquire()
        return self

    async def __aexit__(self, *args: object) -> None:
        return None
