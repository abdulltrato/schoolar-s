$composeFile = Join-Path (Split-Path $PSScriptRoot -Parent) "docker-compose.yml"
. (Join-Path $PSScriptRoot "assert-docker.ps1")

docker compose -f $composeFile exec db psql -U schoolar -d schoolar
