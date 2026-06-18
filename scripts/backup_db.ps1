Param(
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [string]$OutDir = $env:BACKUP_DIR
)

if (-not $DatabaseUrl) {
    Write-Error "DATABASE_URL not set"
    exit 1
}

if (-not $OutDir) { $OutDir = Join-Path -Path (Get-Location) -ChildPath backups }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$ts = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$file = Join-Path $OutDir "db_backup_$ts.sql.gz"

Write-Output "Backing up DB to $file"
pg_dump $DatabaseUrl | gzip > $file
Write-Output "Backup saved: $file"
