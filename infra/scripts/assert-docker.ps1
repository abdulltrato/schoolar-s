$dockerCommand = Get-Command docker -ErrorAction SilentlyContinue

if (-not $dockerCommand) {
    throw @"
Docker CLI nao foi encontrado no PATH.

Instale o Docker Desktop e abra um novo terminal antes de executar este script.
Depois valide com:
  docker --version
  docker compose version
"@
}
