from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional

from app.core.types import ApplicationStatus, utc_now_iso


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)
    updated_at: Mapped[str] = mapped_column(
        String(40),
        default=utc_now_iso,
        onupdate=utc_now_iso,
        nullable=False,
    )


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    role_tags: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    parsed_data: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    embedding: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    is_active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    scores: Mapped[List["OpportunityScore"]] = relationship(back_populates="resume")
    applications: Mapped[List["Application"]] = relationship(back_populates="resume")
    skill_gaps: Mapped[List["SkillGap"]] = relationship(back_populates="resume")
    learning_plans: Mapped[List["LearningPlan"]] = relationship(back_populates="resume")


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    hq_location: Mapped[Optional[str]] = mapped_column(String(255))
    india_presence: Mapped[int] = mapped_column(Integer, default=0)
    company_type: Mapped[Optional[str]] = mapped_column(String(80))
    employee_count: Mapped[Optional[str]] = mapped_column(String(80))
    funding_stage: Mapped[Optional[str]] = mapped_column(String(80))
    tech_stack: Mapped[str] = mapped_column(Text, default="[]")
    culture_tags: Mapped[str] = mapped_column(Text, default="[]")
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    research_data: Mapped[str] = mapped_column(Text, default="{}")
    last_researched: Mapped[Optional[str]] = mapped_column(String(40))

    opportunities: Mapped[List["Opportunity"]] = relationship(back_populates="company")

    __table_args__ = (Index("idx_companies_domain", "domain", unique=True),)


class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    role_type: Mapped[str] = mapped_column(String(80), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    location_type: Mapped[str] = mapped_column(String(40), nullable=False)
    country: Mapped[str] = mapped_column(String(120), default="India", nullable=False)
    job_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[str] = mapped_column(Text, default="[]")
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    posted_date: Mapped[Optional[str]] = mapped_column(String(40))
    deadline: Mapped[Optional[str]] = mapped_column(String(40))
    stipend_min: Mapped[Optional[int]] = mapped_column(Integer)
    stipend_max: Mapped[Optional[int]] = mapped_column(Integer)
    duration_months: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    company: Mapped[Optional["Company"]] = relationship(back_populates="opportunities")
    scores: Mapped[List["OpportunityScore"]] = relationship(back_populates="opportunity")
    applications: Mapped[List["Application"]] = relationship(back_populates="opportunity")
    skill_gaps: Mapped[List["SkillGap"]] = relationship(back_populates="opportunity")

    __table_args__ = (
        Index("idx_opp_company", "company_id"),
        Index("idx_opp_role_type", "role_type"),
        Index("idx_opp_country", "country"),
        Index("idx_opp_posted", "posted_date"),
    )


class OpportunityScore(Base):
    __tablename__ = "opportunity_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    score_band: Mapped[str] = mapped_column(String(80), nullable=False)
    resume_match: Mapped[float] = mapped_column(Float, nullable=False)
    hiring_probability: Mapped[float] = mapped_column(Float, nullable=False)
    location_preference: Mapped[float] = mapped_column(Float, nullable=False)
    freshness: Mapped[float] = mapped_column(Float, nullable=False)
    company_quality: Mapped[float] = mapped_column(Float, nullable=False)
    competition_estimate: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text)
    scored_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)

    opportunity: Mapped["Opportunity"] = relationship(back_populates="scores")
    resume: Mapped["Resume"] = relationship(back_populates="scores")

    __table_args__ = (
        UniqueConstraint("opportunity_id", "resume_id"),
        Index("idx_scores_total", "total_score"),
    )


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default=ApplicationStatus.DISCOVERED.value,
        nullable=False,
    )
    applied_date: Mapped[Optional[str]] = mapped_column(String(40))
    response_date: Mapped[Optional[str]] = mapped_column(String(40))
    offer_date: Mapped[Optional[str]] = mapped_column(String(40))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    source: Mapped[Optional[str]] = mapped_column(String(120))
    referral_contact: Mapped[Optional[str]] = mapped_column(String(255))

    opportunity: Mapped["Opportunity"] = relationship(back_populates="applications")
    resume: Mapped["Resume"] = relationship(back_populates="applications")
    events: Mapped[List["ApplicationEvent"]] = relationship(back_populates="application")
    outreach_messages: Mapped[List["OutreachMessage"]] = relationship(back_populates="application")

    __table_args__ = (
        UniqueConstraint("opportunity_id", "resume_id"),
        Index("idx_apps_status", "status"),
        Index("idx_apps_applied_date", "applied_date"),
    )


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(40))
    to_status: Mapped[Optional[str]] = mapped_column(String(40))
    details: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)

    application: Mapped["Application"] = relationship(back_populates="events")


class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    message_type: Mapped[str] = mapped_column(String(80), nullable=False)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(255))
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255))
    recipient_title: Mapped[Optional[str]] = mapped_column(String(255))
    subject: Mapped[Optional[str]] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_sent: Mapped[int] = mapped_column(Integer, default=0)
    sent_at: Mapped[Optional[str]] = mapped_column(String(40))
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)

    application: Mapped["Application"] = relationship(back_populates="outreach_messages")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    opportunity_id: Mapped[Optional[int]] = mapped_column(ForeignKey("opportunities.id"))
    skill: Mapped[str] = mapped_column(String(120), nullable=False)
    gap_type: Mapped[str] = mapped_column(String(40), nullable=False)
    importance: Mapped[str] = mapped_column(String(40), nullable=False)
    resources: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)

    resume: Mapped["Resume"] = relationship(back_populates="skill_gaps")
    opportunity: Mapped[Optional["Opportunity"]] = relationship(back_populates="skill_gaps")

    __table_args__ = (UniqueConstraint("resume_id", "opportunity_id", "skill"),)


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    week_start: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    report_data: Mapped[str] = mapped_column(Text, nullable=False)
    telegram_sent: Mapped[int] = mapped_column(Integer, default=0)
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)


class TelegramSubscription(Base):
    __tablename__ = "telegram_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    digest_time: Mapped[str] = mapped_column(String(5), default="08:00")
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)


class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[Optional[int]] = mapped_column(ForeignKey("resumes.id"))
    opportunity_id: Mapped[Optional[int]] = mapped_column(ForeignKey("opportunities.id"))
    steps: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)

    # relationships optional
    resume: Mapped[Optional["Resume"]] = relationship(back_populates="learning_plans")
    opportunity: Mapped[Optional["Opportunity"]] = relationship()


class JobRun(Base):
    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="running", nullable=False)
    started_at: Mapped[str] = mapped_column(String(40), default=utc_now_iso, nullable=False)
    finished_at: Mapped[Optional[str]] = mapped_column(String(40))
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    processed_count: Mapped[Optional[int]] = mapped_column(Integer)
    scored_count: Mapped[Optional[int]] = mapped_column(Integer)
    error: Mapped[Optional[str]] = mapped_column(Text)
    cancel_requested: Mapped[int] = mapped_column(Integer, default=0)


class SchedulerLock(Base):
    __tablename__ = "scheduler_locks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String(255))
    acquired_at: Mapped[Optional[str]] = mapped_column(String(40))
    expires_at: Mapped[Optional[str]] = mapped_column(String(40))


