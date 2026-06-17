from app.database.repositories.application_repository import ApplicationRepository
from app.database.repositories.company_repository import CompanyRepository
from app.database.repositories.opportunity_repository import OpportunityRepository
from app.database.repositories.outreach_repository import OutreachRepository
from app.database.repositories.report_repository import ReportRepository
from app.database.repositories.resume_repository import ResumeRepository
from app.database.repositories.score_repository import ScoreRepository
from app.database.repositories.skill_gap_repository import SkillGapRepository

__all__ = [
    "ApplicationRepository",
    "CompanyRepository",
    "OpportunityRepository",
    "OutreachRepository",
    "ReportRepository",
    "ResumeRepository",
    "ScoreRepository",
    "SkillGapRepository",
]
