$ErrorActionPreference = "Stop"

$composeFile = Join-Path (Split-Path $PSScriptRoot -Parent) "docker-compose.yml"

docker compose -f $composeFile up --build
