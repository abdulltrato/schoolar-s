import { MetricCard } from "@/components/metric-card";
import { SectionTitle } from "@/components/section-title";
import { StatusCard } from "@/components/status-card";
import {
  type Aluno,
  type Avaliacao,
  type CollectionSnapshot,
  type Matricula,
  type Progressao,
  type Turma,
  getPlatformSnapshot,
} from "@/lib/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
  }).format(new Date(value));
}

function formatStudentLine(aluno: Aluno) {
  return `Classe ${aluno.classe} | Ciclo ${aluno.ciclo} | ${aluno.estado}`;
}

function formatEvaluationAxes(avaliacao: Avaliacao) {
  const axes = [];

  if (avaliacao.conhecimentos) {
    axes.push("conhecimentos");
  }

  if (avaliacao.habilidades) {
    axes.push("habilidades");
  }

  if (avaliacao.atitudes) {
    axes.push("atitudes");
  }

  return axes.join(", ");
}

function toneForCollection(snapshot: CollectionSnapshot<unknown>) {
  return snapshot.ok ? "success" : "warning";
}

function statusForCollection(snapshot: CollectionSnapshot<unknown>) {
  if (snapshot.requiresAuth) {
    return "AUTH";
  }

  if (snapshot.ok) {
    return "ONLINE";
  }

  return "OFFLINE";
}

type RecordListProps<T> = {
  title: string;
  subtitle: string;
  snapshot: CollectionSnapshot<T>;
  rows: T[];
  renderRow: (row: T) => React.ReactNode;
};

function RecordList<T>({
  title,
  subtitle,
  snapshot,
  rows,
  renderRow,
}: RecordListProps<T>) {
  return (
    <article className="rounded-[1.5rem] border border-ink/10 bg-sand p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-2xl font-semibold text-ink">{title}</h3>
          <p className="mt-2 text-sm leading-6 text-ink/70">{subtitle}</p>
        </div>
        <span className="rounded-full border border-ink/10 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-ink/70">
          {snapshot.count}
        </span>
      </div>

      <p className="mt-4 text-sm leading-6 text-ink/70">{snapshot.message}</p>

      <div className="mt-5 space-y-3">
        {rows.length > 0 ? (
          rows.map(renderRow)
        ) : (
          <div className="rounded-[1rem] border border-dashed border-ink/15 px-4 py-5 text-sm leading-6 text-ink/55">
            Nada para mostrar nesta secao.
          </div>
        )}
      </div>
    </article>
  );
}

export default async function Home() {
  const snapshot = await getPlatformSnapshot();
  const authNotice = snapshot.authConfigured
    ? "Credenciais de leitura configuradas no frontend."
    : "Sem credenciais configuradas. Endpoints protegidos vao responder 401.";

  return (
    <main className="relative overflow-hidden">
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-grid bg-[size:34px_34px] opacity-40"
      />
      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8 sm:px-10 lg:px-12">
        <header className="mb-10 rounded-[2rem] border border-white/60 bg-white/80 p-8 shadow-card backdrop-blur">
          <div className="mb-8 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="mb-3 inline-flex rounded-full border border-ink/10 bg-ember/10 px-4 py-1 text-sm font-semibold uppercase tracking-[0.25em] text-ember">
                Substrato Educacao
              </p>
              <h1 className="font-display text-4xl font-bold leading-tight text-ink sm:text-5xl lg:text-6xl">
                Painel operacional ligado aos recursos reais do backend.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-ink/75 sm:text-lg">
                A pagina agora consome alunos, turmas, matriculas, avaliacoes e
                progressoes diretamente da API Django em vez de mostrar apenas
                blocos estaticos.
              </p>
            </div>
            <div className="rounded-[1.5rem] bg-ink px-6 py-5 text-sand shadow-card">
              <p className="text-xs uppercase tracking-[0.3em] text-sand/70">
                Backend alvo
              </p>
              <p className="mt-2 max-w-sm font-display text-2xl font-semibold">
                {snapshot.baseUrlLabel}
              </p>
              <p className="mt-2 max-w-xs text-sm leading-6 text-sand/75">
                {authNotice}
              </p>
              <p className="mt-2 max-w-xs text-sm leading-6 text-sand/60">
                Tenant: {snapshot.tenantId || "nao configurado"}
              </p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-4 xl:grid-cols-5">
            <MetricCard
              label="Alunos"
              value={String(snapshot.alunos.count)}
              detail="Registos lidos de /api/v1/academico/alunos/."
            />
            <MetricCard
              label="Turmas"
              value={String(snapshot.turmas.count)}
              detail="Turmas ativas e respetivo ciclo letivo."
            />
            <MetricCard
              label="Matriculas"
              value={String(snapshot.matriculas.count)}
              detail="Ligacao real entre alunos e turmas."
            />
            <MetricCard
              label="Avaliacoes"
              value={String(snapshot.avaliacoes.count)}
              detail="Lancamentos de avaliacao vindos da API."
            />
            <MetricCard
              label="Progressoes"
              value={String(snapshot.progressoes.count)}
              detail="Decisoes de progressao carregadas do backend."
            />
          </div>
        </header>

        <section className="mb-10 grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
          <div className="rounded-[2rem] border border-ink/10 bg-white/80 p-8 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Conectividade"
              title="Estado da plataforma e da leitura de dados"
              description="Health e readiness continuam em tempo real, mas agora acompanhados pelo estado de cada colecao funcional."
            />
            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <StatusCard
                title="Healthcheck"
                status={snapshot.health.status}
                tone={snapshot.health.ok ? "success" : "warning"}
                body={snapshot.health.message}
              />
              <StatusCard
                title="Readiness"
                status={snapshot.readiness.status}
                tone={snapshot.readiness.ok ? "success" : "warning"}
                body={snapshot.readiness.message}
              />
              <StatusCard
                title="Alunos API"
                status={statusForCollection(snapshot.alunos)}
                tone={toneForCollection(snapshot.alunos)}
                body={snapshot.alunos.message}
              />
              <StatusCard
                title="Turmas API"
                status={statusForCollection(snapshot.turmas)}
                tone={toneForCollection(snapshot.turmas)}
                body={snapshot.turmas.message}
              />
              <StatusCard
                title="Avaliacoes API"
                status={statusForCollection(snapshot.avaliacoes)}
                tone={toneForCollection(snapshot.avaliacoes)}
                body={snapshot.avaliacoes.message}
              />
              <StatusCard
                title="Progressoes API"
                status={statusForCollection(snapshot.progressoes)}
                tone={toneForCollection(snapshot.progressoes)}
                body={snapshot.progressoes.message}
              />
            </div>
          </div>

          <div className="rounded-[2rem] border border-ink/10 bg-ink p-8 text-sand shadow-card">
            <SectionTitle
              eyebrow="Configuracao"
              title="Contrato minimo para consumo real"
              description="Se o backend exigir autenticacao, o frontend server-side pode enviar Basic Auth e tenant header."
              inverse
            />
            <div className="mt-6 space-y-3 text-sm leading-6 text-sand/78">
              <p>
                Base URL: <code>{snapshot.baseUrlLabel}</code>
              </p>
              <p>
                Credenciais: <code>API_USERNAME</code> e <code>API_PASSWORD</code>
              </p>
              <p>
                Tenant opcional: <code>API_TENANT_ID</code>
              </p>
              <p>
                Publico no browser: <code>NEXT_PUBLIC_API_BASE_URL</code>
              </p>
            </div>
          </div>
        </section>

        <section className="mb-10 grid gap-6 lg:grid-cols-2">
          <RecordList
            title="Alunos recentes"
            subtitle="Primeiros registos retornados pelo endpoint academico, incluindo competencias agregadas."
            snapshot={snapshot.alunos}
            rows={snapshot.alunos.items.slice(0, 5)}
            renderRow={(aluno) => (
              <div
                key={aluno.id}
                className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{aluno.nome}</p>
                  <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ink/70">
                    {aluno.competencias.length} competencias
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  {formatStudentLine(aluno)}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">
                  Nascimento: {formatDate(aluno.data_nascimento)}
                </p>
              </div>
            )}
          />

          <RecordList
            title="Turmas e matriculas"
            subtitle="Turmas reais expostas pela API, com professor responsavel quando disponivel."
            snapshot={snapshot.turmas}
            rows={snapshot.turmas.items.slice(0, 5)}
            renderRow={(turma) => {
              const matriculasDaTurma = snapshot.matriculas.items.filter(
                (matricula: Matricula) => matricula.turma === turma.id,
              ).length;

              return (
                <div
                  key={turma.id}
                  className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-ink">{turma.nome}</p>
                    <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ink/70">
                      {matriculasDaTurma} matriculas
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-ink/70">
                    Ciclo {turma.ciclo} | Ano letivo {turma.ano_letivo}
                  </p>
                  <p className="mt-1 text-sm leading-6 text-ink/55">
                    Professor: {turma.professor_responsavel_nome || "nao atribuido"}
                  </p>
                </div>
              );
            }}
          />
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <RecordList
            title="Avaliacoes recentes"
            subtitle="Lancamentos de avaliacao reais, com tipo, competencia e eixos avaliados."
            snapshot={snapshot.avaliacoes}
            rows={snapshot.avaliacoes.items.slice(0, 5)}
            renderRow={(avaliacao) => (
              <div
                key={avaliacao.id}
                className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">
                    {avaliacao.aluno_nome || `Aluno #${avaliacao.aluno}`}
                  </p>
                  <span className="rounded-full bg-ember/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ember">
                    {avaliacao.tipo}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  Competencia: {avaliacao.competencia_nome || avaliacao.competencia}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">
                  Data: {formatDate(avaliacao.data)} | Nota: {avaliacao.nota || "sem nota"}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">
                  Eixos: {formatEvaluationAxes(avaliacao)}
                </p>
              </div>
            )}
          />

          <RecordList
            title="Progressoes recentes"
            subtitle="Decisoes de progressao devolvidas pelo backend para o ciclo e ano letivo."
            snapshot={snapshot.progressoes}
            rows={snapshot.progressoes.items.slice(0, 5)}
            renderRow={(progressao) => (
              <div
                key={progressao.id}
                className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">
                    {progressao.aluno_nome || `Aluno #${progressao.aluno}`}
                  </p>
                  <span className="rounded-full bg-fern/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-fern">
                    {progressao.decisao}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  Ciclo {progressao.ciclo} | Ano letivo {progressao.ano_letivo}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">
                  Data da decisao: {formatDate(progressao.data_decisao)}
                </p>
              </div>
            )}
          />
        </section>
      </div>
    </main>
  );
}
