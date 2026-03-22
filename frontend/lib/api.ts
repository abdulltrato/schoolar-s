type HealthPayload = {
  status?: string;
};

type ReadinessPayload = {
  status?: string;
  checks?: Record<string, string>;
};

type PaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

type AlunoCompetencia = {
  id: number;
  competencia: number;
  competencia_nome: string;
  nivel: string;
  data_atualizacao: string;
};

export type Aluno = {
  id: number;
  nome: string;
  data_nascimento: string;
  classe: number;
  ciclo: number;
  estado: string;
  competencias: AlunoCompetencia[];
};

export type Turma = {
  id: number;
  nome: string;
  ciclo: number;
  ano_letivo: string;
  professor_responsavel: number | null;
  professor_responsavel_nome?: string;
};

export type Matricula = {
  id: number;
  aluno: number;
  aluno_nome?: string;
  turma: number;
  turma_nome?: string;
  data_matricula: string;
};

export type Avaliacao = {
  id: number;
  aluno: number;
  aluno_nome?: string;
  competencia: number;
  competencia_nome?: string;
  tipo: string;
  data: string;
  nota: string | null;
  comentario: string;
  conhecimentos: boolean;
  habilidades: boolean;
  atitudes: boolean;
};

export type Progressao = {
  id: number;
  aluno: number;
  aluno_nome?: string;
  ciclo: number;
  ano_letivo: string;
  data_decisao: string;
  decisao: string;
  comentario: string;
};

type EndpointSnapshot = {
  ok: boolean;
  status: string;
  message: string;
};

export type CollectionSnapshot<T> = {
  ok: boolean;
  status: string;
  statusCode: number;
  count: number;
  items: T[];
  message: string;
  requiresAuth: boolean;
};

export type PlatformSnapshot = {
  baseUrlLabel: string;
  authConfigured: boolean;
  tenantId: string | null;
  health: EndpointSnapshot;
  readiness: EndpointSnapshot;
  alunos: CollectionSnapshot<Aluno>;
  turmas: CollectionSnapshot<Turma>;
  matriculas: CollectionSnapshot<Matricula>;
  avaliacoes: CollectionSnapshot<Avaliacao>;
  progressoes: CollectionSnapshot<Progressao>;
};

function resolveApiBaseUrl() {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

function resolveTenantId() {
  return process.env.API_TENANT_ID || process.env.NEXT_PUBLIC_TENANT_ID || null;
}

function resolveBasicAuthHeader() {
  const username = process.env.API_USERNAME;
  const password = process.env.API_PASSWORD;

  if (!username || !password) {
    return null;
  }

  return `Basic ${Buffer.from(`${username}:${password}`).toString("base64")}`;
}

function buildHeaders() {
  const headers = new Headers({
    Accept: "application/json",
  });

  const authHeader = resolveBasicAuthHeader();
  const tenantId = resolveTenantId();

  if (authHeader) {
    headers.set("Authorization", authHeader);
  }

  if (tenantId) {
    headers.set("X-Tenant-ID", tenantId);
  }

  return headers;
}

async function parseJsonSafe<T>(response: Response): Promise<T | undefined> {
  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    return undefined;
  }

  try {
    return (await response.json()) as T;
  } catch {
    return undefined;
  }
}

async function readJson<T>(
  path: string,
): Promise<{ ok: boolean; statusCode: number; data?: T }> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      cache: "no-store",
      headers: buildHeaders(),
    });

    const data = await parseJsonSafe<T>(response);
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

function normalizeCollection<T>(payload?: PaginatedResponse<T> | T[]) {
  if (Array.isArray(payload)) {
    return {
      count: payload.length,
      items: payload,
    };
  }

  if (payload?.results) {
    return {
      count: payload.count ?? payload.results.length,
      items: payload.results,
    };
  }

  return {
    count: 0,
    items: [] as T[],
  };
}

function getCollectionMessage(statusCode: number, count: number) {
  if (statusCode === 401 || statusCode === 403) {
    return "Endpoint protegido. Configure API_USERNAME/API_PASSWORD para leitura autenticada.";
  }

  if (statusCode === 0) {
    return "Sem conexao com o backend.";
  }

  if (count === 0) {
    return "Endpoint acessivel, mas sem registos para mostrar.";
  }

  return `${count} registos carregados do backend.`;
}

async function readCollection<T>(
  path: string,
): Promise<CollectionSnapshot<T>> {
  const response = await readJson<PaginatedResponse<T> | T[]>(path);
  const normalized = normalizeCollection(response.data);
  const ok = response.ok;

  return {
    ok,
    status:
      response.statusCode === 401 || response.statusCode === 403
        ? "AUTH"
        : ok
          ? "ONLINE"
          : "OFFLINE",
    statusCode: response.statusCode,
    count: normalized.count,
    items: normalized.items,
    message: getCollectionMessage(response.statusCode, normalized.count),
    requiresAuth: response.statusCode === 401 || response.statusCode === 403,
  };
}

export async function getPlatformSnapshot(): Promise<PlatformSnapshot> {
  const [
    healthResponse,
    readinessResponse,
    alunos,
    turmas,
    matriculas,
    avaliacoes,
    progressoes,
  ] = await Promise.all([
    readJson<HealthPayload>("/health/"),
    readJson<ReadinessPayload>("/ready/"),
    readCollection<Aluno>("/api/v1/academico/alunos/"),
    readCollection<Turma>("/api/v1/escola/turmas/"),
    readCollection<Matricula>("/api/v1/escola/matriculas/"),
    readCollection<Avaliacao>("/api/v1/avaliacao/avaliacoes/"),
    readCollection<Progressao>("/api/v1/progresso/progressoes/"),
  ]);

  const baseUrl = resolveApiBaseUrl();

  return {
    baseUrlLabel: baseUrl,
    authConfigured: Boolean(resolveBasicAuthHeader()),
    tenantId: resolveTenantId(),
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
    alunos,
    turmas,
    matriculas,
    avaliacoes,
    progressoes,
  };
}
