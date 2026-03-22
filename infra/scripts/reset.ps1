$ErrorActionPreference = "Stop"

$composeFile = Join-Path (Split-Path $PSScriptRoot -Parent) "docker-compose.yml"
. (Join-Path $PSScriptRoot "assert-docker.ps1")

docker compose -f $composeFile down -v --remove-orphans

Write-Output "Ambiente Docker resetado com volumes removidos."
