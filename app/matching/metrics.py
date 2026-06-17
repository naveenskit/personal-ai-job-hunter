from __future__ import annotations

from collections import defaultdict

_counters: dict[str, int] = defaultdict(int)

# Job status
_job_status: dict[str, str | float | bool | None] = {
    "last_run": None,
    "last_duration": None,
    "running": False,
    "last_error": None,
}


def inc_counter(name: str, value: int = 1) -> None:
    _counters[name] += int(value)
    # update prometheus metric if available
    try:
        if _PROM_AVAILABLE and name in _PROM_COUNTERS:
            _PROM_COUNTERS[name].inc(int(value))
    except Exception:
        pass


def get_metrics() -> dict[str, int]:
    return dict(_counters)


def job_start() -> None:
    _job_status["running"] = True
    _job_status["last_error"] = None
    try:
        if _PROM_AVAILABLE:
            _PROM_GAUGES["job_running"].set(1)
    except Exception:
        pass


def job_end(duration: float, processed: int | None = None, scored: int | None = None) -> None:
    _job_status["running"] = False
    _job_status["last_duration"] = float(duration)
    from app.core.types import utc_now_iso

    _job_status["last_run"] = utc_now_iso()
    if processed is not None:
        inc_counter("last_processed")
    if scored is not None:
        inc_counter("last_scored")
    try:
        if _PROM_AVAILABLE:
            _PROM_GAUGES["job_running"].set(0)
            _PROM_GAUGES["last_duration_seconds"].set(float(duration))
            if processed is not None:
                if _PROM_COUNTERS.get("last_processed"):
                    _PROM_COUNTERS["last_processed"].inc(processed)
            if scored is not None:
                if _PROM_COUNTERS.get("last_scored"):
                    _PROM_COUNTERS["last_scored"].inc(scored)
    except Exception:
        pass


def job_error(err: str) -> None:
    _job_status["running"] = False
    _job_status["last_error"] = err
    try:
        if _PROM_AVAILABLE:
            _PROM_GAUGES["job_running"].set(0)
            _PROM_INFO["last_error"].info({"error": str(err)})
    except Exception:
        pass


def get_job_status() -> dict[str, str | float | bool | None]:
    return dict(_job_status)


# Prometheus integration (optional)
try:
    from prometheus_client import Counter, Gauge, Info

    _PROM_AVAILABLE = True
    _PROM_COUNTERS: dict[str, Counter] = {
        "bulk_runs": Counter(
            "matching_bulk_runs_total",
            "Number of bulk matching runs",
        ),
        "matches_scored": Counter(
            "matching_matches_scored_total",
            "Number of matches scored",
        ),
        "last_processed": Counter(
            "matching_last_processed_total",
            "Last processed count (cumulative)",
        ),
    }
    _PROM_GAUGES: dict[str, Gauge] = {
        "job_running": Gauge(
            "matching_job_running",
            "Is job currently running (1/0)",
        ),
        "last_duration_seconds": Gauge(
            "matching_job_last_duration_seconds",
            "Last run duration seconds",
        ),
    }
    _PROM_INFO: dict[str, Info] = {
        "last_error": Info("matching_job_last_error", "Last job run error message"),
    }
except Exception:
    _PROM_AVAILABLE = False
    _PROM_COUNTERS = {}
    _PROM_GAUGES = {}
    _PROM_INFO = {}
