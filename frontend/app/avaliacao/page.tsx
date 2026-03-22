import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import {
  type Avaliacao,
  type ComponenteAvaliativa,
  type PeriodoAvaliativo,
  type ResultadoPeriodoDisciplina,
  getAvaliacaoSnapshot,
} from "@/lib/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
  }).format(new Date(value));
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

  return axes.length > 0 ? axes.join(", ") : "sem eixos complementares";
}

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(
  value: string | string[] | undefined,
) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export default async function AvaliacaoPage({ searchParams }: PageProps) {
  const snapshot = await getAvaliacaoSnapshot();
  const params = (await searchParams) || {};
  const ano = readParam(params.ano);
  const periodo = readParam(params.periodo);
  const turma = readParam(params.turma);

  const periodos = snapshot.periodos.items.filter((item) => {
    if (ano && item.ano_letivo_codigo !== ano) {
      return false;
    }
    if (periodo && String(item.id) !== periodo) {
      return false;
    }
    return true;
  });

  const componentes = snapshot.componentes.items.filter((item) => {
    if (ano && item.ano_letivo !== ano) {
      return false;
    }
    if (periodo && String(item.periodo) !== periodo) {
      return false;
    }
    return true;
  });

  const avaliacoes = snapshot.avaliacoes.items.filter((item) => {
    if (ano && item.ano_letivo !== ano) {
      return false;
    }
    if (periodo && String(item.periodo) !== periodo) {
      return false;
    }
    if (turma && item.turma_nome !== turma) {
      return false;
    }
    return true;
  });

  const resultados = snapshot.resultadosPeriodo.items.filter((item) => {
    if (periodo && String(item.periodo) !== periodo) {
      return false;
    }
    if (turma && item.turma_nome !== turma) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Avaliacao"
      description="Periodos, componentes, lancamentos e resultados finais por disciplina."
    >
      <FilterBar
        fields={[
          {
            name: "ano",
            label: "Ano Letivo",
            value: ano,
            options: snapshot.anosLetivos.items.map((item) => ({
              value: item.codigo,
              label: item.codigo,
            })),
          },
          {
            name: "periodo",
            label: "Periodo",
            value: periodo,
            options: snapshot.periodos.items.map((item) => ({
              value: String(item.id),
              label: item.nome,
            })),
          },
          {
            name: "turma",
            label: "Turma",
            value: turma,
            options: Array.from(new Set(snapshot.turmas.items.map((item) => item.nome))).map((item) => ({
              value: item,
              label: item,
            })),
          },
        ]}
      />

      <section className="grid gap-6 lg:grid-cols-2">
        <RecordList
          title="Periodos avaliativos"
          subtitle="Calendario oficial de avaliacao por ano letivo."
          snapshot={snapshot.periodos}
          rows={periodos.slice(0, 6)}
          renderRow={(periodo: PeriodoAvaliativo) => {
            const componentesDoPeriodo = snapshot.componentes.items.filter(
              (componente: ComponenteAvaliativa) => componente.periodo === periodo.id,
            ).length;

            return (
              <div key={periodo.id} className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{periodo.nome}</p>
                  <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ink/70">
                    ordem {periodo.ordem}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  {periodo.ano_letivo_codigo} | {formatDate(periodo.data_inicio)} ate {formatDate(periodo.data_fim)}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">{componentesDoPeriodo} componentes neste periodo.</p>
              </div>
            );
          }}
        />

        <RecordList
          title="Componentes avaliativas"
          subtitle="Instrumentos usados no calculo das medias por disciplina."
          snapshot={snapshot.componentes}
          rows={componentes.slice(0, 8)}
          renderRow={(componente: ComponenteAvaliativa) => (
            <div key={componente.id} className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{componente.nome}</p>
                <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ink/70">
                  {componente.tipo}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {componente.disciplina_nome} | {componente.periodo_nome}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                Peso {componente.peso} | Nota maxima {componente.nota_maxima}
              </p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <RecordList
          title="Lancamentos"
          subtitle="Avaliacoes disciplinares com periodo, componente e eixos."
          snapshot={snapshot.avaliacoes}
          rows={avaliacoes.slice(0, 8)}
          renderRow={(avaliacao: Avaliacao) => (
            <div key={avaliacao.id} className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{avaliacao.aluno_nome}</p>
                <span className="rounded-full bg-ember/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ember">
                  {avaliacao.tipo}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {avaliacao.disciplina_nome} | {avaliacao.turma_nome}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {avaliacao.periodo_nome || "Sem periodo"} | {avaliacao.componente_nome || "Sem componente"} | Nota: {avaliacao.nota || "sem nota"}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">Eixos: {formatEvaluationAxes(avaliacao)}</p>
            </div>
          )}
        />

        <RecordList
          title="Resultados por disciplina"
          subtitle="Medias finais ponderadas por periodo e disciplina."
          snapshot={snapshot.resultadosPeriodo}
          rows={resultados.slice(0, 8)}
          renderRow={(resultado: ResultadoPeriodoDisciplina) => (
            <div key={resultado.id} className="rounded-[1rem] border border-ink/10 bg-white px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{resultado.aluno_nome}</p>
                <span className="rounded-full bg-fern/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-fern">
                  media {resultado.media_final}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {resultado.disciplina_nome} | {resultado.periodo_nome}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {resultado.turma_nome} | {resultado.avaliacoes_consideradas} avaliacoes consideradas
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
