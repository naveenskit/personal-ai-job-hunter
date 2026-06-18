Param()

Write-Host "This PowerShell helper sets GitHub Actions secrets using the 'gh' CLI.`n"
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI 'gh' not found. Install from https://cli.github.com/"
    exit 1
}

$repo = (gh repo view --json nameWithOwner -q .nameWithOwner)
Write-Host "Repository: $repo"

# Example usage: set environment variables first, then run this script.
gh secret set DATABASE_URL --body $env:DATABASE_URL
gh secret set GHCR_PAT --body $env:GHCR_PAT
gh secret set DOCKER_USERNAME --body $env:DOCKER_USERNAME
gh secret set DOCKER_PASSWORD --body $env:DOCKER_PASSWORD
gh secret set APP_SECRET_KEY --body $env:APP_SECRET_KEY

Write-Host "Secrets configured. Verify in repository settings -> Secrets & variables -> Actions."
