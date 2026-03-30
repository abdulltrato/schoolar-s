import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { formatAssessmentType } from "@/lib/labels";
import {
  type Assessment,
  type AssessmentComponent,
  type AssessmentPeriod,
  type SubjectPeriodResult,
  getAssessmentSnapshot,
  requireAuthSession,
} from "@/lib/api";

// Formata datas ISO para dd/mmm/aaaa em pt-PT.
function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
  }).format(new Date(value));
}

function formatEvaluationAxes(assessment: Assessment) {
  const axes = [];

  if (assessment.knowledge) {
    axes.push("Conhecimentos");
  }

  if (assessment.skills) {
    axes.push("Habilidades");
  }

  if (assessment.attitudes) {
    axes.push("Atitudes");
  }

  return axes.length > 0 ? axes.join(", ") : "sem eixos complementares";
}

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

const panelClass = "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/95 p-4 shadow-[0_18px_50px_rgba(20,33,61,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_22px_55px_rgba(20,33,61,0.16)]";
const badgeClass = "rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70";
function readParam(
  value: string | string[] | undefined,
) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export default async function AssessmentPage({ searchParams }: PageProps) {
  await requireAuthSession("/assessment");
  const snapshot = await getAssessmentSnapshot();
  const params = (await searchParams) || {};
  const year = readParam(params.year);
  const period = readParam(params.period);
  const classroom = readParam(params.classroom);

  const periods = snapshot.periods.items.filter((item) => {
    if (year && item.academic_year_code !== year) {
      return false;
    }
    if (period && String(item.id) !== period) {
      return false;
    }
    return true;
  });

  const components = snapshot.components.items.filter((item) => {
    if (year && item.academic_year_code !== year) {
      return false;
    }
    if (period && String(item.period) !== period) {
      return false;
    }
    return true;
  });

  const assessments = snapshot.assessments.items.filter((item) => {
    if (year && item.academic_year_code !== year) {
      return false;
    }
    if (period && String(item.period) !== period) {
      return false;
    }
    if (classroom && item.classroom_name !== classroom) {
      return false;
    }
    return true;
  });

  const results = snapshot.periodResults.items.filter((item) => {
    if (period && String(item.period) !== period) {
      return false;
    }
    if (classroom && item.classroom_name !== classroom) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Avaliação"
      description="Períodos, componentes, registos e resultados finais por disciplina."
      aside={(
        <>
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Resumo"
              title="Panorama avaliativo"
              description="Leitura compacta dos períodos e resultados disponíveis."
            />
            <dl className="mt-5 space-y-4 text-sm leading-6">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Períodos</dt>
                <dd className="text-lg font-semibold">{periods.length} listados</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Registos</dt>
                <dd className="text-lg font-semibold">{assessments.length} avaliações</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Resultados</dt>
                <dd className="text-lg font-semibold">{results.length} médias</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária de avaliação" className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-white/85 p-4 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/60">Secções</p>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#periods">
                  Períodos e componentes
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#results">
                  Avaliações e resultados
                </a>
              </li>
            </ul>
          </nav>
        </>
      )}
    >
      <section className="overflow-hidden rounded-[1.5rem] border border-white/65 bg-[linear-gradient(135deg,rgba(20,33,61,0.95),rgba(32,52,85,0.9))] p-5 text-sand shadow-card shadow-[0_30px_80px_rgba(20,33,61,0.18)]">
        <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Avaliação</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Períodos, componentes e resultados prontos para análise.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Visualize os calendários avaliativos, os instrumentos associados e as médias finais. Os filtros mantêm o foco em um ciclo letivo, período ou turma específicos.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Períodos</p>
              <p className="mt-2 font-display text-2xl font-semibold">{periods.length}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Componentes</p>
              <p className="mt-2 font-display text-2xl font-semibold">{components.length}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Resultados</p>
              <p className="mt-2 font-display text-2xl font-semibold">{results.length}</p>
            </div>
          </div>
        </div>
      </section>

      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_20px_55px_rgba(20,33,61,0.08)]">
        <p className="text-sm text-ink/70">
          Recorte atual — ano: {year || "todos"} · período: {period || "todos"} · turma: {classroom || "todas"}.
        </p>
      </div>

      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_50px_rgba(20,33,61,0.06)]">
        <FilterBar
        fields={[
          {
            name: "year",
            label: "Ano letivo",
            value: year,
            options: snapshot.academicYears.items.map((item) => ({
              value: item.code,
              label: item.code,
            })),
          },
          {
            name: "period",
            label: "Período",
            value: period,
            options: snapshot.periods.items.map((item) => ({
              value: String(item.id),
              label: item.name,
            })),
          },
          {
            name: "classroom",
            label: "Turma",
            value: classroom,
            options: Array.from(new Set(snapshot.classrooms.items.map((item) => item.name))).map((item) => ({
              value: item,
              label: item,
            })),
          },
        ]}
      />
      </div>

      <section id="periods" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Períodos de avaliação"
          subtitle="Calendário oficial de avaliação por ano letivo."
          snapshot={snapshot.periods}
          rows={periods.slice(0, 6)}
          renderRow={(period: AssessmentPeriod) => {
            const periodComponents = snapshot.components.items.filter(
              (component: AssessmentComponent) => component.period === period.id,
            ).length;

            return (
              <div key={period.id} className={panelClass}>
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{period.name}</p>
                  <span className={badgeClass}>
                    ordem {period.order}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  {period.academic_year_code} · {formatDate(period.start_date)} a {formatDate(period.end_date)}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">{periodComponents} componentes neste período.</p>
              </div>
            );
          }}
        />

        <RecordList
          title="Componentes avaliativas"
          subtitle="Instrumentos usados para calcular médias por disciplina."
          snapshot={snapshot.components}
          rows={components.slice(0, 8)}
          renderRow={(component: AssessmentComponent) => (
            <div key={component.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{component.name}</p>
                <span className={badgeClass}>
                  {formatAssessmentType(component.type)}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {component.subject_name} · {component.period_name}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                Peso {component.weight} · Nota máxima {component.max_score}
              </p>
            </div>
          )}
        />
      </section>

      <section id="results" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Avaliações"
          subtitle="Avaliações por disciplina com período, componente e eixos."
          snapshot={snapshot.assessments}
          rows={assessments.slice(0, 8)}
          renderRow={(assessment: Assessment) => (
          <div key={assessment.id} className={panelClass}>
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-ink">{assessment.student_name}</p>
              <span className={badgeClass}>
                {formatAssessmentType(assessment.type)}
              </span>
            </div>
            <p className="mt-2 text-sm leading-6 text-ink/70">
              {assessment.subject_name} · {assessment.classroom_name}
            </p>
            <p className="mt-1 text-sm leading-6 text-ink/55">
              {assessment.period_name || "Sem período"} · {assessment.component_name || "Sem componente"} · Nota: {assessment.score ?? "sem nota"}
            </p>
            <p className="mt-1 text-sm leading-6 text-ink/55">Eixos: {formatEvaluationAxes(assessment)}</p>
          </div>
          )}
        />

        <RecordList
          title="Resultados por disciplina"
          subtitle="Médias finais ponderadas por período e disciplina."
          snapshot={snapshot.periodResults}
          rows={results.slice(0, 8)}
          renderRow={(result: SubjectPeriodResult) => (
            <div key={result.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{result.student_name}</p>
                <span className={badgeClass}>
                  média {result.final_average}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {result.subject_name} · {result.period_name}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {result.classroom_name} · {result.assessments_counted} avaliações contabilizadas
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
