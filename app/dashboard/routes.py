from flask import Blueprint, render_template

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard", template_folder="templates")


@bp.get("/")
def dashboard_home():
    """Render a minimal dashboard skeleton."""
    return render_template("dashboard.html")
