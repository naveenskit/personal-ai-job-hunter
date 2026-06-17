from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal, TypeAlias

JSONValue: TypeAlias = str | int | float | bool | None | dict[str, Any] | list[Any]
JSONDict: TypeAlias = dict[str, JSONValue]


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_iso() -> str:
    return utc_now().isoformat()


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class ApplicationStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    RESEARCHED = "RESEARCHED"
    MATCHED = "MATCHED"
    OUTREACH_SENT = "OUTREACH_SENT"
    APPLIED = "APPLIED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INTERVIEWING = "INTERVIEWING"
    OFFERED = "OFFERED"
    REJECTED = "REJECTED"
    GHOSTED = "GHOSTED"
    WITHDRAWN = "WITHDRAWN"


class ScoreBand(StrEnum):
    DREAM_MATCH = "Dream Match"
    EXCELLENT = "Excellent Match"
    STRONG = "Strong Match"
    GOOD = "Good Match"
    LOW = "Low Priority"


RoleType: TypeAlias = Literal["intern", "new_grad", "associate"]
LocationType: TypeAlias = Literal["onsite", "remote", "hybrid"]


@dataclass(slots=True)
class AgentResult:
    name: str
    success: bool
    started_at: datetime
    finished_at: datetime
    processed: int = 0
    created: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JobQuery:
    keywords: list[str]
    locations: list[str]
    role_types: list[str]
    remote: bool = True


@dataclass(slots=True)
class RawOpportunity:
    title: str
    company_name: str
    location: str
    job_url: str
    source: str
    description: str | None = None
    posted_date: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
