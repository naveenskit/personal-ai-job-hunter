from __future__ import annotations

import asyncio
import threading
import time

from app.ai.provider import get_ai_provider
from app.database.connection import session_scope
from app.matching import metrics
from app.matching.job import run_bulk_matching
from config.settings import get_settings


def start_scheduler() -> None:
    settings = get_settings()
    # don't start scheduler during tests
    if settings.environment == "test":
        return

    interval = 60 * 60  # default 1h

    async def _worker() -> None:
        while True:
            metrics.job_start()
            start = time.time()
            try:
                ai = get_ai_provider()
                async with session_scope() as session:
                    from app.database.repositories.job_run_repository import JobRunRepository
                    from app.database.repositories.lock_repository import LockRepository

                    # acquire distributed lock so only one instance runs the job
                    lock_repo = LockRepository(session)
                    owner = f"pid:{threading.get_ident()}"
                    acquired = await lock_repo.acquire_lock(
                        "matching_bulk", owner, ttl_seconds=60 * 60
                    )
                    if not acquired:
                        # skip this run, another instance is handling it
                        metrics.job_end(0.0, processed=0, scored=0)
                        await asyncio.sleep(interval)
                        continue

                    jr = JobRunRepository(session)
                    run = await jr.create_run("bulk_matching")

                    # start heartbeat to renew lock while job runs
                    run_done = asyncio.Event()

                    async def _heartbeat(
                        _run_done=run_done,
                        _lock_repo=lock_repo,
                        _owner=owner,
                    ) -> None:
                        try:
                            while not _run_done.is_set():
                                await asyncio.sleep(60 * 15)
                                try:
                                    await _lock_repo.renew_lock(
                                        "matching_bulk", _owner, ttl_seconds=60 * 60
                                    )
                                except Exception:
                                    # heartbeat failures are non-fatal
                                    pass
                        except asyncio.CancelledError:
                            return

                    hb = asyncio.create_task(_heartbeat())
                    try:
                        processed, scored = await run_bulk_matching(session, ai, job_run_id=run.id)
                    finally:
                        run_done.set()
                        hb.cancel()
                        # release lock
                        await lock_repo.release_lock("matching_bulk", owner)
                    duration = time.time() - start
                    # mark_finished called inside run_bulk_matching, but ensure metrics updated
                    metrics.job_end(duration, processed, scored)
                    metrics.inc_counter("bulk_runs")
            except Exception as e:  # broad catch to protect scheduler
                metrics.job_error(str(e))
            await asyncio.sleep(interval)

    def _thread_main() -> None:
        asyncio.run(_worker())

    t = threading.Thread(target=_thread_main, daemon=True, name="matching-scheduler")
    t.start()
