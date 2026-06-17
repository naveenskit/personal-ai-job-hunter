<#
PowerShell helper to install GitHub CLI (if missing), authenticate, push current branch,
and create a PR. Run from repository root.
Usage:
  powershell -ExecutionPolicy Bypass -File .\scripts\push_and_pr.ps1
Optional parameters:
  -RepoUrl <string>   # remote URL (HTTPS or SSH). If omitted, uses current origin.
  -Branch <string>    # branch to push. If omitted, uses current git branch.
  -Base <string>      # PR base branch (default: main)
  -Title <string>     # PR title
  -BodyFile <string>  # Path to file containing PR body
#>
param(
    [string]$RepoUrl = '',
    [string]$Branch = '',
    [string]$Base = 'main',
    [string]$Title = '',
    [string]$BodyFile = '.\\files\\PR_BODY.md'
)

function Write-ErrAndExit($msg, $code=1){ Write-Host $msg -ForegroundColor Red; exit $code }

# Ensure we're in a git repo
if (-not (Test-Path .git)) { Write-ErrAndExit "Not a git repository. Run this from repository root." }

# Resolve branch
if (-not $Branch) {
    $Branch = (git rev-parse --abbrev-ref HEAD) -replace '\r','' -replace '\n',''
}
Write-Host "Branch: $Branch"

# Optionally set remote
if ($RepoUrl) {
    if ((git remote) -notcontains 'origin') {
        git remote add origin $RepoUrl
    } else {
        git remote set-url origin $RepoUrl
    }
    Write-Host "Remote 'origin' set to $RepoUrl"
}

# Check for gh
$ghPath = (Get-Command gh -ErrorAction SilentlyContinue).Path
if (-not $ghPath) {
    Write-Host "GitHub CLI (gh) not found. Attempting to install via winget..."
    try {
        winget install --id GitHub.cli -e -h
        $ghPath = (Get-Command gh -ErrorAction SilentlyContinue).Path
    } catch {
        Write-Host "winget install failed or not available. You can continue with SSH instead." -ForegroundColor Yellow
    }
}

# If gh found, ensure auth
if ($ghPath) {
    Write-Host "Found gh: $ghPath"
    $authStatus = & gh auth status 2>&1
    if ($LASTEXITCODE -ne 0 -or $authStatus -match 'You are not logged in') {
        Write-Host "Please complete interactive login in the browser..."
        & gh auth login --web
        if ($LASTEXITCODE -ne 0) { Write-Host "gh auth login failed or cancelled." -ForegroundColor Yellow }
    } else {
        Write-Host "gh authentication looks OK."
    }
}

# Attempt push
Write-Host "Pushing branch to origin..."
$pushOutput = git push -u origin $Branch 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed:" -ForegroundColor Red
    Write-Host $pushOutput
    Write-Host "Common fixes: run 'gh auth login --web' if using HTTPS, or switch remote to SSH and add your public key to GitHub." -ForegroundColor Yellow
    Write-Host "If you have cached wrong credentials, open Windows Credential Manager and remove any GitHub entries, then retry." -ForegroundColor Yellow
    exit 2
}
Write-Host "Push succeeded."

# Create PR if gh is available
if ($ghPath) {
    if (-not $Title) {
        $Title = "Consolidate outreach code"
    }
    $body = ''
    if (Test-Path $BodyFile) { $body = Get-Content $BodyFile -Raw }
    Write-Host "Creating PR via gh..."
    $args = @('pr','create','--base',$Base,'--head',$Branch,'--title',$Title)
    if ($body) { $args += @('--body',$body) }
    & gh @args
    if ($LASTEXITCODE -ne 0) {
        Write-Host "gh pr create failed. You can open the PR manually at https://github.com/<owner>/<repo>/pulls" -ForegroundColor Yellow
        exit 3
    }
    Write-Host "PR created (or opened interactively)."
} else {
    Write-Host "gh CLI not available — PR not created automatically. Open a PR in the GitHub web UI." -ForegroundColor Yellow
}

Write-Host "Done." -ForegroundColor Green
