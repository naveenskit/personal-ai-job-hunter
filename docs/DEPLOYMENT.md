# Deployment runbook

This document describes basic steps to build and deploy the Personal AI Job Hunter application.

Local Docker build and run

1. Build image locally:

```bash
docker build -t jobhunter:latest .
```

2. Run with Docker Compose:

```bash
docker-compose up -d --build
```

3. Check logs:

```bash
docker-compose logs -f web
```

Production notes

- The app uses SQLite by default. For production, replace `DATABASE_URL` with a managed PostgreSQL/PostGIS URL and configure `config/settings.py` accordingly.
- Run Alembic migrations on startup or via CI prior to swapping traffic.
- Use a process manager or container platform (ECS, Kubernetes, Heroku) for production deployments.

Monitoring & Healthchecks

- A Prometheus-compatible metrics endpoint is available at `/metrics` (Prometheus client is installed).
- Expose `/api/v1/health` for simple liveness checks.
- Use a metrics exporter and an alerting policy for error rates, latency, and scheduler failures.

TLS

- For production, terminate TLS at a reverse proxy (NGINX, Traefik) or use platform-managed TLS (ECS ALB, Cloud Run, Heroku).
- Ensure `ENVIRONMENT=production` and secure `APP_SECRET_KEY` and `API_SECRET_KEY` via secrets.

CI/CD

- `./.github/workflows/deploy.yml` builds and pushes an image to GHCR on pushes to `main`.
- Grant `GITHUB_TOKEN` package write permissions are required (handled by default in the workflow).
