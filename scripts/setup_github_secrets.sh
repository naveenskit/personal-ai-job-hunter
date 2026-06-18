#!/usr/bin/env bash
# Example script to set repository secrets using the GitHub CLI (`gh`).
# Replace the placeholder values or supply them via environment variables.

set -euo pipefail

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

echo "Setting GitHub Actions secrets for $REPO"

# Example secrets — replace values before running
gh secret set DATABASE_URL --body "$DATABASE_URL"
gh secret set GHCR_PAT --body "$GHCR_PAT"
gh secret set DOCKER_USERNAME --body "$DOCKER_USERNAME"
gh secret set DOCKER_PASSWORD --body "$DOCKER_PASSWORD"
gh secret set APP_SECRET_KEY --body "$APP_SECRET_KEY"

echo "Secrets set. Verify in repository settings -> Secrets & variables -> Actions."
