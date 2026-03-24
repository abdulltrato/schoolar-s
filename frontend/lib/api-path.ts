export function resolveApiBaseUrl() {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

export function resolveApiVersion() {
  return process.env.API_VERSION || process.env.NEXT_PUBLIC_API_VERSION || "v1";
}

export function apiPath(path: string, version = resolveApiVersion()) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `/api/${version}${normalized}`;
}
