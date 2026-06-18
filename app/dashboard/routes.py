from flask import Blueprint, render_template, jsonify
from sqlalchemy import select, func

from app.database.connection import session_scope
from app.database.models import (
    Resume,
    Company,
    Opportunity,
    Application,
    WeeklyReport,
    JobRun,
)


bp = Blueprint("dashboard", __name__, url_prefix="/dashboard", template_folder="templates")


@bp.get("/")
def dashboard_home():
    """Render a minimal dashboard skeleton."""
    return render_template("dashboard.html")


@bp.get("/api/stats")
async def dashboard_stats():
    """Return basic counts for dashboard panels."""
    async with session_scope() as session:
        q = select(
            func.count(Resume.id),
            func.count(Company.id),
            func.count(Opportunity.id),
            func.count(Application.id),
            func.count(WeeklyReport.id),
            func.count(JobRun.id),
        )
        result = await session.execute(q)
        counts = result.one()

    return jsonify(
        {
            "resumes": counts[0],
            "companies": counts[1],
            "opportunities": counts[2],
            "applications": counts[3],
            "weekly_reports": counts[4],
            "job_runs": counts[5],
        }
    )
