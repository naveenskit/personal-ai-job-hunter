import asyncio

from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from flask import Response

from app.core.logging import configure_logging, get_logger
from app.database.connection import init_db
from app.resumes.routes import resumes_bp
from config.settings import get_settings


def create_app() -> Flask:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.app_secret_key.get_secret_value()
    app.register_blueprint(resumes_bp)
    try:
        # opportunites and companies blueprints are optional during early phases
        from app.opportunities.routes import opps_bp

        app.register_blueprint(opps_bp)
    except Exception:
        pass

    try:
        from app.companies.routes import companies_bp

        app.register_blueprint(companies_bp)
    except Exception:
        pass
    try:
        # skills blueprint added in Phase 10
        from app.skills.routes import bp as skills_bp

        app.register_blueprint(skills_bp)
    except Exception:
        pass
    try:
        # research blueprint for Phase 4
        from app.research.routes import bp as research_bp

        app.register_blueprint(research_bp)
    except Exception:
        pass
    try:
        # matching blueprint for Phase 5
        from app.matching.routes import bp as matching_bp

        app.register_blueprint(matching_bp)
    except Exception:
        pass
    try:
        # outreach blueprint for Phase 7
        from app.outreach.routes import bp as outreach_bp

        app.register_blueprint(outreach_bp)
    except Exception:
        pass
    try:
        # start background scheduler for periodic tasks
        from app.matching.scheduler import start_scheduler

        start_scheduler()
    except Exception:
        # scheduler failures are non-fatal during startup
        pass
    try:
        # learning blueprint for Phase 9
        from app.learning.routes import bp as learning_bp

        app.register_blueprint(learning_bp)
    except Exception:
        pass

    try:
        # dashboard blueprint (Phase 13)
        from app.dashboard.routes import bp as dashboard_bp

        app.register_blueprint(dashboard_bp)
    except Exception:
        pass

    @app.get("/api/v1/health")
    def health() -> tuple[dict[str, object], int]:
        return (
            {
                "success": True,
                "data": {
                    "status": "ok",
                    "environment": settings.environment,
                },
                "error": None,
            },
            200,
        )

    # Prometheus metrics endpoint
    REQUEST_COUNTER = Counter("jobhunter_requests_total", "Total HTTP requests")

    @app.get("/metrics")
    def metrics():
        REQUEST_COUNTER.inc()
        data = generate_latest()
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    @app.get("/")
    def index() -> tuple[dict[str, object], int]:
        return jsonify({"service": "Personal AI Job Hunter", "status": "ok"}), 200

    return app


async def bootstrap() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    await init_db()
    logger.info("database_initialized")


if __name__ == "__main__":
    asyncio.run(bootstrap())
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=get_settings().environment == "development")
