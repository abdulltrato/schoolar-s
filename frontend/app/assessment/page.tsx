import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import {
  type Assessment,
  type AssessmentComponent,
  type AssessmentPeriod,
  type SubjectPeriodResult,
  getAssessmentSnapshot,
  requireAuthSession,
} from "@/lib/api";

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
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Resumo"
              title="Panorama avaliativo"
              description="Leitura compacta dos períodos e resultados disponíveis."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Períodos</dt>
                <dd>{periods.length} períodos no recorte atual.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Registos</dt>
                <dd>{assessments.length} avaliações visíveis.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Resultados</dt>
                <dd>{results.length} médias calculadas.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária de avaliação" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#periods">Períodos e componentes</a></li>
              <li><a href="#results">Avaliações e resultados</a></li>
            </ul>
          </nav>
        </>
      )}
    >
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
              <div key={period.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{period.name}</p>
                  <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                    ordem {period.order}
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-5 text-ink/70">
                  {period.academic_year_code} | {formatDate(period.start_date)} a {formatDate(period.end_date)}
                </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">{periodComponents} componentes neste período.</p>
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
            <div key={component.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{component.name}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {component.type}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {component.subject_name} | {component.period_name}
              </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">
                  Peso {component.weight} | Nota máxima {component.max_score}
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
            <div key={assessment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{assessment.student_name}</p>
                <span className="rounded-full bg-ember/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ember">
                  {assessment.type}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {assessment.subject_name} | {assessment.classroom_name}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {assessment.period_name || "Sem período"} | {assessment.component_name || "Sem componente"} | Nota: {assessment.score ?? "sem nota"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Eixos: {formatEvaluationAxes(assessment)}</p>
            </div>
          )}
        />

        <RecordList
          title="Resultados por disciplina"
          subtitle="Médias finais ponderadas por período e disciplina."
          snapshot={snapshot.periodResults}
          rows={results.slice(0, 8)}
          renderRow={(result: SubjectPeriodResult) => (
            <div key={result.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{result.student_name}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  média {result.final_average}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {result.subject_name} | {result.period_name}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {result.classroom_name} | {result.assessments_counted} avaliações contabilizadas
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
