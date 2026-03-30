// Resolve a base URL para chamadas de API, caindo para localhost em desenvolvimento.
export function resolveApiBaseUrl() {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

// Retorna a versão de API configurada (default v1).
export function resolveApiVersion() {
  return process.env.API_VERSION || process.env.NEXT_PUBLIC_API_VERSION || "v1";
}

// Monta o caminho completo para um endpoint, normalizando barra inicial.
export function apiPath(path: string, version = resolveApiVersion()) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `/api/${version}${normalized}`;
}
