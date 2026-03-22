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

export type AlunoCompetencia = {
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

export type AnoLetivo = {
  id: number;
  codigo: string;
  data_inicio: string;
  data_fim: string;
  ativo: boolean;
};

export type Classe = {
  id: number;
  numero: number;
  ciclo: number;
  nome: string;
};

export type Escola = {
  id: number;
  codigo: string;
  nome: string;
  distrito: string;
  provincia: string;
  ativa: boolean;
};

export type Professor = {
  id: number;
  user: number;
  escola: number | null;
  escola_nome?: string;
  nome: string;
  especialidade: string;
};

export type Turma = {
  id: number;
  nome: string;
  escola: number | null;
  escola_nome?: string;
  classe: number;
  classe_nome?: string;
  ciclo: number;
  ano_letivo: string;
  professor_responsavel: number | null;
  professor_responsavel_nome?: string;
};

export type DisciplinaClasse = {
  id: number;
  ano_letivo: string;
  classe: number;
  disciplina: number;
  disciplina_nome?: string;
  carga_horaria_semanal: number;
};

export type AlocacaoDocente = {
  id: number;
  professor: number;
  professor_nome?: string;
  turma: number;
  turma_nome?: string;
  escola_nome?: string;
  disciplina_classe: number;
  disciplina_nome?: string;
  ano_letivo?: string;
  classe?: number;
};

export type Matricula = {
  id: number;
  aluno: number;
  aluno_nome?: string;
  turma: number;
  turma_nome?: string;
  data_matricula: string;
  escola_nome?: string;
  ano_letivo?: string;
  classe?: number;
};

export type AtribuicaoGestao = {
  id: number;
  professor: number;
  professor_nome?: string;
  escola: number;
  escola_nome?: string;
  ano_letivo: number;
  ano_letivo_codigo?: string;
  cargo: string;
  classe: number | null;
  classe_numero?: number;
  turma: number | null;
  turma_nome?: string;
  ciclo: number | null;
  ativo: boolean;
};

export type PlanoCurricularDisciplina = {
  id: number;
  disciplina_classe: number;
  disciplina_nome?: string;
  classe?: number;
  ano_letivo?: string;
  objetivos: string;
  metodologia: string;
  criterios_avaliacao: string;
  ativo: boolean;
  competencias_previstas: Array<{ id: number; nome: string }>;
};

export type PeriodoAvaliativo = {
  id: number;
  ano_letivo: number;
  ano_letivo_codigo?: string;
  nome: string;
  ordem: number;
  data_inicio: string;
  data_fim: string;
  ativo: boolean;
};

export type ComponenteAvaliativa = {
  id: number;
  periodo: number;
  periodo_nome?: string;
  disciplina_classe: number;
  disciplina_nome?: string;
  classe?: number;
  ano_letivo?: string;
  tipo: string;
  nome: string;
  peso: string;
  nota_maxima: string;
  obrigatoria: boolean;
};

export type Avaliacao = {
  id: number;
  aluno: number;
  aluno_nome?: string;
  alocacao_docente: number | null;
  periodo: number | null;
  periodo_nome?: string;
  componente: number | null;
  componente_nome?: string;
  competencia: number | null;
  competencia_nome?: string;
  professor_nome?: string;
  turma_nome?: string;
  disciplina_nome?: string;
  ano_letivo?: string;
  classe?: number;
  tipo: string;
  data: string;
  nota: string | null;
  comentario: string;
  conhecimentos: boolean;
  habilidades: boolean;
  atitudes: boolean;
};

export type ResultadoPeriodoDisciplina = {
  id: number;
  aluno: number;
  aluno_nome?: string;
  alocacao_docente: number;
  professor_nome?: string;
  turma_nome?: string;
  disciplina_nome?: string;
  periodo: number;
  periodo_nome?: string;
  media_final: string;
  avaliacoes_consideradas: number;
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
  anosLetivos: CollectionSnapshot<AnoLetivo>;
  classes: CollectionSnapshot<Classe>;
  escolas: CollectionSnapshot<Escola>;
  professores: CollectionSnapshot<Professor>;
  turmas: CollectionSnapshot<Turma>;
  disciplinasClasse: CollectionSnapshot<DisciplinaClasse>;
  alocacoesDocentes: CollectionSnapshot<AlocacaoDocente>;
  matriculas: CollectionSnapshot<Matricula>;
  atribuicoesGestao: CollectionSnapshot<AtribuicaoGestao>;
  planosDisciplina: CollectionSnapshot<PlanoCurricularDisciplina>;
  periodos: CollectionSnapshot<PeriodoAvaliativo>;
  componentes: CollectionSnapshot<ComponenteAvaliativa>;
  avaliacoes: CollectionSnapshot<Avaliacao>;
  resultadosPeriodo: CollectionSnapshot<ResultadoPeriodoDisciplina>;
};

type PlatformMeta = {
  baseUrlLabel: string;
  authConfigured: boolean;
  tenantId: string | null;
  health: EndpointSnapshot;
  readiness: EndpointSnapshot;
};

export type HomeSnapshot = PlatformMeta & {
  escolas: CollectionSnapshot<Escola>;
  atribuicoesGestao: CollectionSnapshot<AtribuicaoGestao>;
  planosDisciplina: CollectionSnapshot<PlanoCurricularDisciplina>;
  periodos: CollectionSnapshot<PeriodoAvaliativo>;
  componentes: CollectionSnapshot<ComponenteAvaliativa>;
  resultadosPeriodo: CollectionSnapshot<ResultadoPeriodoDisciplina>;
};

export type GestaoSnapshot = PlatformMeta & {
  anosLetivos: CollectionSnapshot<AnoLetivo>;
  escolas: CollectionSnapshot<Escola>;
  turmas: CollectionSnapshot<Turma>;
  matriculas: CollectionSnapshot<Matricula>;
  atribuicoesGestao: CollectionSnapshot<AtribuicaoGestao>;
};

export type CurriculoSnapshot = PlatformMeta & {
  anosLetivos: CollectionSnapshot<AnoLetivo>;
  classes: CollectionSnapshot<Classe>;
  disciplinasClasse: CollectionSnapshot<DisciplinaClasse>;
  planosDisciplina: CollectionSnapshot<PlanoCurricularDisciplina>;
};

export type AvaliacaoSnapshot = PlatformMeta & {
  anosLetivos: CollectionSnapshot<AnoLetivo>;
  turmas: CollectionSnapshot<Turma>;
  periodos: CollectionSnapshot<PeriodoAvaliativo>;
  componentes: CollectionSnapshot<ComponenteAvaliativa>;
  avaliacoes: CollectionSnapshot<Avaliacao>;
  resultadosPeriodo: CollectionSnapshot<ResultadoPeriodoDisciplina>;
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

async function readJsonWithRetry<T>(
  path: string,
  attempts = 2,
): Promise<{ ok: boolean; statusCode: number; data?: T }> {
  let lastResponse = { ok: false, statusCode: 0 } as {
    ok: boolean;
    statusCode: number;
    data?: T;
  };

  for (let attempt = 0; attempt < attempts; attempt += 1) {
    lastResponse = await readJson<T>(path);
    if (lastResponse.ok || lastResponse.statusCode === 401 || lastResponse.statusCode === 403) {
      return lastResponse;
    }
  }

  return lastResponse;
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

async function readCollection<T>(path: string): Promise<CollectionSnapshot<T>> {
  const response = await readJsonWithRetry<PaginatedResponse<T> | T[]>(path);
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

async function getPlatformMeta(): Promise<PlatformMeta> {
  const [healthResponse, readinessResponse] = await Promise.all([
    readJsonWithRetry<HealthPayload>("/health/"),
    readJsonWithRetry<ReadinessPayload>("/ready/"),
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
  };
}

export async function getPlatformSnapshot(): Promise<PlatformSnapshot> {
  const meta = await getPlatformMeta();
  const [
    alunos,
    anosLetivos,
    classes,
    escolas,
    professores,
    turmas,
    disciplinasClasse,
    alocacoesDocentes,
    matriculas,
    atribuicoesGestao,
    planosDisciplina,
    periodos,
    componentes,
    avaliacoes,
    resultadosPeriodo,
  ] = await Promise.all([
    readCollection<Aluno>("/api/v1/academico/alunos/"),
    readCollection<AnoLetivo>("/api/v1/escola/anos-letivos/"),
    readCollection<Classe>("/api/v1/escola/classes/"),
    readCollection<Escola>("/api/v1/escola/escolas/"),
    readCollection<Professor>("/api/v1/escola/professores/"),
    readCollection<Turma>("/api/v1/escola/turmas/"),
    readCollection<DisciplinaClasse>("/api/v1/escola/disciplinas-classe/"),
    readCollection<AlocacaoDocente>("/api/v1/escola/alocacoes-docentes/"),
    readCollection<Matricula>("/api/v1/escola/matriculas/"),
    readCollection<AtribuicaoGestao>("/api/v1/escola/atribuicoes-gestao/"),
    readCollection<PlanoCurricularDisciplina>("/api/v1/curriculo/planos-disciplina/"),
    readCollection<PeriodoAvaliativo>("/api/v1/avaliacao/periodos/"),
    readCollection<ComponenteAvaliativa>("/api/v1/avaliacao/componentes/"),
    readCollection<Avaliacao>("/api/v1/avaliacao/avaliacoes/"),
    readCollection<ResultadoPeriodoDisciplina>("/api/v1/avaliacao/resultados-periodo/"),
  ]);

  return {
    ...meta,
    alunos,
    anosLetivos,
    classes,
    escolas,
    professores,
    turmas,
    disciplinasClasse,
    alocacoesDocentes,
    matriculas,
    atribuicoesGestao,
    planosDisciplina,
    periodos,
    componentes,
    avaliacoes,
    resultadosPeriodo,
  };
}

export async function getHomeSnapshot(): Promise<HomeSnapshot> {
  const meta = await getPlatformMeta();
  const [
    escolas,
    atribuicoesGestao,
    planosDisciplina,
    periodos,
    componentes,
    resultadosPeriodo,
  ] = await Promise.all([
    readCollection<Escola>("/api/v1/escola/escolas/"),
    readCollection<AtribuicaoGestao>("/api/v1/escola/atribuicoes-gestao/"),
    readCollection<PlanoCurricularDisciplina>("/api/v1/curriculo/planos-disciplina/"),
    readCollection<PeriodoAvaliativo>("/api/v1/avaliacao/periodos/"),
    readCollection<ComponenteAvaliativa>("/api/v1/avaliacao/componentes/"),
    readCollection<ResultadoPeriodoDisciplina>("/api/v1/avaliacao/resultados-periodo/"),
  ]);

  return {
    ...meta,
    escolas,
    atribuicoesGestao,
    planosDisciplina,
    periodos,
    componentes,
    resultadosPeriodo,
  };
}

export async function getGestaoSnapshot(): Promise<GestaoSnapshot> {
  const meta = await getPlatformMeta();
  const [anosLetivos, escolas, turmas, matriculas, atribuicoesGestao] = await Promise.all([
    readCollection<AnoLetivo>("/api/v1/escola/anos-letivos/"),
    readCollection<Escola>("/api/v1/escola/escolas/"),
    readCollection<Turma>("/api/v1/escola/turmas/"),
    readCollection<Matricula>("/api/v1/escola/matriculas/"),
    readCollection<AtribuicaoGestao>("/api/v1/escola/atribuicoes-gestao/"),
  ]);

  return {
    ...meta,
    anosLetivos,
    escolas,
    turmas,
    matriculas,
    atribuicoesGestao,
  };
}

export async function getCurriculoSnapshot(): Promise<CurriculoSnapshot> {
  const meta = await getPlatformMeta();
  const [anosLetivos, classes, disciplinasClasse, planosDisciplina] = await Promise.all([
    readCollection<AnoLetivo>("/api/v1/escola/anos-letivos/"),
    readCollection<Classe>("/api/v1/escola/classes/"),
    readCollection<DisciplinaClasse>("/api/v1/escola/disciplinas-classe/"),
    readCollection<PlanoCurricularDisciplina>("/api/v1/curriculo/planos-disciplina/"),
  ]);

  return {
    ...meta,
    anosLetivos,
    classes,
    disciplinasClasse,
    planosDisciplina,
  };
}

export async function getAvaliacaoSnapshot(): Promise<AvaliacaoSnapshot> {
  const meta = await getPlatformMeta();
  const [anosLetivos, turmas, periodos, componentes, avaliacoes, resultadosPeriodo] = await Promise.all([
    readCollection<AnoLetivo>("/api/v1/escola/anos-letivos/"),
    readCollection<Turma>("/api/v1/escola/turmas/"),
    readCollection<PeriodoAvaliativo>("/api/v1/avaliacao/periodos/"),
    readCollection<ComponenteAvaliativa>("/api/v1/avaliacao/componentes/"),
    readCollection<Avaliacao>("/api/v1/avaliacao/avaliacoes/"),
    readCollection<ResultadoPeriodoDisciplina>("/api/v1/avaliacao/resultados-periodo/"),
  ]);

  return {
    ...meta,
    anosLetivos,
    turmas,
    periodos,
    componentes,
    avaliacoes,
    resultadosPeriodo,
  };
}
