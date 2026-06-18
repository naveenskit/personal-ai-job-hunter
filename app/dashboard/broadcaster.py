import asyncio
from typing import Set

_subscribers: Set[asyncio.Queue] = set()


async def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.add(q)
    return q


async def unsubscribe(q: asyncio.Queue) -> None:
    try:
        _subscribers.discard(q)
    except Exception:
        pass


def publish(event: dict) -> None:
    # publish synchronously to all subscriber queues
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            # ignore failed subscriber
            try:
                _subscribers.discard(q)
            except Exception:
                pass
