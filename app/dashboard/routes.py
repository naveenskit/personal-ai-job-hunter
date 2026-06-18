from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
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
from config.settings import get_settings
from app.core.types import utc_now_iso
from pydantic import SecretStr


bp = Blueprint("dashboard", __name__, url_prefix="/dashboard", template_folder="templates", static_folder="static")


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


def _check_dashboard_auth(request) -> bool:
    settings = get_settings()
    token: SecretStr | None = settings.dashboard_token
    if token is None:
        return True
    # allow session-based auth (for browser)
    if session.get("dashboard_authed"):
        return True
    header = request.headers.get("X-DASHBOARD-TOKEN")
    if header is not None and header == token.get_secret_value():
        return True
    return False



@bp.before_app_request
def _dashboard_before_request():
    # Only enforce for dashboard blueprint routes when a token is configured
    settings = get_settings()
    if settings.dashboard_token is None:
        return
    # allow static and login/logout endpoints without auth
    path = request.path or ""
    if path.startswith(url_for('dashboard.static', filename='')):
        return
    if path.startswith(url_for('dashboard.dashboard_home')):
        # dashboard home requires auth; allow check below
        pass
    if path in (url_for('dashboard.login'), url_for('dashboard.logout')):
        return
    # If already authed in session or via header, continue
    if session.get('dashboard_authed'):
        return
    header = request.headers.get('X-DASHBOARD-TOKEN')
    if header and header == settings.dashboard_token.get_secret_value():
        return
    # Otherwise redirect to login for browser requests
    if request.endpoint and request.endpoint.startswith('dashboard.'):
        return redirect(url_for('dashboard.login'))


@bp.get('/login')
def login():
    # render login form
    return render_template('login.html')


@bp.post('/login')
def login_post():
    settings = get_settings()
    if settings.dashboard_token is None:
        return redirect(url_for('dashboard.dashboard_home'))
    pw = request.form.get('password')
    if pw is None:
        return render_template('login.html', error='Missing password')
    if pw == settings.dashboard_token.get_secret_value():
        session['dashboard_authed'] = True
        return redirect(url_for('dashboard.dashboard_home'))
    return render_template('login.html', error='Invalid password')


@bp.get('/logout')
def logout():
    session.pop('dashboard_authed', None)
    return redirect(url_for('dashboard.login'))


@bp.get("/api/applications")
async def recent_applications(request=None):
    """Return recent applications for the dashboard table."""
    from flask import request as flask_request

    if not _check_dashboard_auth(flask_request):
        return (jsonify({"error": "unauthorized"}), 401)

    async with session_scope() as session:
        q = select(
            Application.id,
            Application.status,
            Application.applied_date,
            Opportunity.title,
            Company.name,
        ).join(Opportunity, Opportunity.id == Application.opportunity_id, isouter=True)
        q = q.join(Company, Company.id == Opportunity.company_id, isouter=True)
        q = q.order_by(Application.applied_date.desc().nullslast()).limit(20)
        result = await session.execute(q)
        rows = [
            {
                "id": r[0],
                "status": r[1],
                "applied_date": r[2],
                "title": r[3],
                "company": r[4],
            }
            for r in result.fetchall()
        ]

    return jsonify(rows)


@bp.post("/api/run-job")
async def run_job():
    """Manual trigger for a simple job run record (for demo)."""
    from flask import request as flask_request

    if not _check_dashboard_auth(flask_request):
        return (jsonify({"error": "unauthorized"}), 401)

    settings = get_settings()
    job_name = flask_request.json.get("job_name", "manual_trigger")
    async with session_scope() as session:
        jr = JobRun(
            job_name=job_name,
            status="completed",
            started_at=utc_now_iso(),
            finished_at=utc_now_iso(),
            duration_seconds=0,
            processed_count=0,
        )
        session.add(jr)

    return jsonify({"ok": True, "job_name": job_name})
