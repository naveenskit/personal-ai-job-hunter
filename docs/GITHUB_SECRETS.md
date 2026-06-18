Required GitHub Actions Secrets

This project uses GitHub Actions to build and optionally push Docker images. Set the following repository-level secrets in `Settings -> Secrets and variables -> Actions`.

- `GHCR_PAT` — Personal Access Token with `write:packages` and `repo` scopes for pushing to GitHub Container Registry.
- `DOCKER_USERNAME` — Docker Hub username (if using Docker Hub in workflows).
- `DOCKER_PASSWORD` — Docker Hub password or access token.
- `DATABASE_URL` — Production database connection string (e.g., `postgresql://...`).
- `APP_SECRET_KEY` — Flask `SECRET_KEY` for session signing.

Example (using `gh`):

```
export GHCR_PAT=... 
export DOCKER_USERNAME=... 
export DOCKER_PASSWORD=... 
export DATABASE_URL=... 
export APP_SECRET_KEY=... 
./scripts/setup_github_secrets.sh
```

On Windows PowerShell:

```
$env:GHCR_PAT = '...'
$env:DOCKER_USERNAME = '...'
$env:DOCKER_PASSWORD = '...'
$env:DATABASE_URL = '...'
$env:APP_SECRET_KEY = '...'
.\scripts\setup_github_secrets.ps1
```
