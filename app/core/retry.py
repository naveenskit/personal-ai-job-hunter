import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from random import random
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def async_retry(
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as exc:
                    last_error = exc
                    if attempt == attempts:
                        break
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    jitter = delay * 0.2 * random()
                    await asyncio.sleep(delay + jitter)

            if last_error is None:
                raise RuntimeError("retry wrapper failed without an exception")
            raise last_error

        return wrapper

    return decorator
