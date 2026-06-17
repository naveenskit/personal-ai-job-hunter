from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from app.core.types import utc_now_iso
from app.database.repositories.learning_repository import LearningRepository


@dataclass(slots=True)
class LearningStep:
    topic: str
    reason: str
    resource: str


@dataclass(slots=True)
class LearningPlan:
    resume_id: int | None
    opportunity_id: int | None
    steps: list[LearningStep]
    created_at: str


class LearningAgent:
    def __init__(self, session=None) -> None:
        self.session = session
        self.repo = LearningRepository(session) if session is not None else None

    async def create_plan(
        self,
        gaps: list | None = None,
        resume_id: int | None = None,
        opportunity_id: int | None = None,
    ) -> LearningPlan | object:
        steps: list[LearningStep] = []
        if gaps:
            for g in gaps:
                topic = g.get("skill") if isinstance(g, dict) else str(g)
                resource = "https://www.learn.com"
                if isinstance(g, dict) and g.get("resources"):
                    resource = g.get("resources")[0]
                steps.append(
                    LearningStep(topic=topic, reason="Skill gap identified", resource=resource)
                )

        plan = LearningPlan(
            resume_id=resume_id,
            opportunity_id=opportunity_id,
            steps=steps,
            created_at=utc_now_iso(),
        )

        # persist if session/repo available
        if self.repo is not None:
            steps_json = json.dumps([asdict(s) for s in steps])
            item = await self.repo.create_plan(
                resume_id=resume_id, opportunity_id=opportunity_id, steps=steps_json
            )
            return item

        return plan
