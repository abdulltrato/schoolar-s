$ErrorActionPreference = "Stop"

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$composeFile = Join-Path (Split-Path $PSScriptRoot -Parent) "docker-compose.yml"
. (Join-Path $PSScriptRoot "assert-docker.ps1")
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $repoRoot "backups"
$backupFile = Join-Path $backupDir "schoolar-$timestamp.sql"

New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

docker compose -f $composeFile exec -T db pg_dump -U schoolar -d schoolar > $backupFile

Write-Output "Backup criado em: $backupFile"
