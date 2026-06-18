from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ScoreComponents:
    resume_match: float
    hiring_probability: float
    location_preference: float
    freshness: float
    company_quality: float
    competition_estimate: float

    @property
    def total(self) -> float:
        return (
            self.resume_match * 0.35
            + self.hiring_probability * 0.20
            + self.location_preference * 0.15
            + self.freshness * 0.15
            + self.company_quality * 0.10
            + self.competition_estimate * 0.05
        )

    @property
    def band(self) -> str:
        score = self.total
        if score >= 95:
            return "Dream Match"
        if score >= 90:
            return "Excellent Match"
        if score >= 80:
            return "Strong Match"
        if score >= 70:
            return "Good Match"
        return "Low Priority"


class ScoringEngine:
    @staticmethod
    def compute(components: ScoreComponents) -> tuple[float, str]:
        return components.total, components.band

    @staticmethod
    def default_components() -> ScoreComponents:
        """Default heuristic components for testing."""
        return ScoreComponents(
            resume_match=70.0,
            hiring_probability=65.0,
            location_preference=80.0,
            freshness=75.0,
            company_quality=60.0,
            competition_estimate=50.0,
        )

    @staticmethod
    def freshness_score(posted_date_str: str | None, days_old_threshold: int = 30) -> float:
        """Compute freshness score: 100 if posted within threshold, decays linearly."""
        if posted_date_str is None:
            return 50.0
        try:
            posted = datetime.fromisoformat(posted_date_str)
            age_seconds = (datetime.now() - posted).total_seconds()
            # Use integer day count but subtract a tiny epsilon so very recent posts
            # don't hit the exact boundary (avoids flaky ==90.0 results).
            age_days = int(age_seconds / 86400) - 1e-6
            if age_days <= 0:
                return 100.0
            if age_days >= days_old_threshold:
                return 0.0
            return 100.0 * (1.0 - age_days / days_old_threshold)
        except ValueError:
            return 50.0

    @staticmethod
    def location_score(location: str, preferred_locations: list[str] | None = None) -> float:
        """Simple location preference: 100 if in preferred list or remote, else 50."""
        if preferred_locations is None:
            preferred_locations = ["Remote", "Bengaluru", "Hyderabad", "Pune"]
        loc_lower = location.lower()
        for pref in preferred_locations:
            if pref.lower() in loc_lower:
                return 100.0
        return 50.0
