type HealthPayload = {
  status?: string;
};

type ReadinessPayload = {
  status?: string;
  checks?: Record<string, string>;
};

type EndpointSnapshot = {
  ok: boolean;
  status: string;
  message: string;
};

type PlatformSnapshot = {
  baseUrlLabel: string;
  health: EndpointSnapshot;
  readiness: EndpointSnapshot;
};

function resolveApiBaseUrl() {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

async function readJson<T>(path: string): Promise<{ ok: boolean; statusCode: number; data?: T }> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    });

    const data = (await response.json()) as T;
    return { ok: response.ok, statusCode: response.status, data };
  } catch {
    return { ok: false, statusCode: 0 };
  }
}

function formatReadinessMessage(payload?: ReadinessPayload) {
  if (!payload?.checks) {
    return "Sem detalhes retornados pelo endpoint de readiness.";
  }

  const summary = Object.entries(payload.checks)
    .map(([key, value]) => `${key}: ${value}`)
    .join(" | ");

  return `Checks reportados: ${summary}.`;
}

export async function getPlatformSnapshot(): Promise<PlatformSnapshot> {
  const healthResponse = await readJson<HealthPayload>("/health/");
  const readinessResponse = await readJson<ReadinessPayload>("/ready/");
  const baseUrl = resolveApiBaseUrl();

  return {
    baseUrlLabel: baseUrl,
    health: {
      ok: healthResponse.ok,
      status: healthResponse.data?.status?.toUpperCase() || "OFFLINE",
      message: healthResponse.ok
        ? "Endpoint respondeu corretamente e a aplicacao esta acessivel."
        : `Nao foi possivel consultar o backend (${healthResponse.statusCode || "sem conexao"}).`,
    },
    readiness: {
      ok: readinessResponse.ok && readinessResponse.data?.status === "ok",
      status: readinessResponse.data?.status?.toUpperCase() || "OFFLINE",
      message:
        readinessResponse.ok && readinessResponse.data
          ? formatReadinessMessage(readinessResponse.data)
          : `Readiness indisponivel (${readinessResponse.statusCode || "sem conexao"}).`,
    },
  };
}
