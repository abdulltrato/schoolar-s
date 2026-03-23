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
} from "@/lib/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
  }).format(new Date(value));
}

function formatEvaluationAxes(assessment: Assessment) {
  const axes = [];

  if (assessment.knowledge) {
    axes.push("knowledge");
  }

  if (assessment.skills) {
    axes.push("skills");
  }

  if (assessment.attitudes) {
    axes.push("attitudes");
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
      title="Assessment"
      description="Periods, components, records, and final results by subject."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Summary"
              title="Assessment Overview"
              description="A compact read of periods and loaded results."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Periods</dt>
                <dd>{periods.length} periods in the current slice.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Records</dt>
                <dd>{assessments.length} visible assessments.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Results</dt>
                <dd>{results.length} calculated averages.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Assessment secondary navigation" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Sections</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#periods">Periods and components</a></li>
              <li><a href="#results">Assessments and results</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      <FilterBar
        fields={[
          {
            name: "year",
            label: "Academic Year",
            value: year,
            options: snapshot.academicYears.items.map((item) => ({
              value: item.code,
              label: item.code,
            })),
          },
          {
            name: "period",
            label: "Periodo",
            value: period,
            options: snapshot.periods.items.map((item) => ({
              value: String(item.id),
              label: item.name,
            })),
          },
          {
            name: "classroom",
            label: "Classroom",
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
          title="Assessment Periods"
          subtitle="Official assessment calendar by academic year."
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
                    order {period.order}
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-5 text-ink/70">
                  {period.academic_year_code} | {formatDate(period.start_date)} to {formatDate(period.end_date)}
                </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">{periodComponents} components in this period.</p>
              </div>
            );
          }}
        />

        <RecordList
          title="Assessment Components"
          subtitle="Instruments used to calculate subject averages."
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
                Weight {component.weight} | Maximum score {component.max_score}
              </p>
            </div>
          )}
        />
      </section>

      <section id="results" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Assessments"
          subtitle="Subject assessments with period, component, and axes."
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
                {assessment.period_name || "No period"} | {assessment.component_name || "No component"} | Score: {assessment.score || "no score"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Axes: {formatEvaluationAxes(assessment)}</p>
            </div>
          )}
        />

        <RecordList
          title="Results by Subject"
          subtitle="Weighted final averages by period and subject."
          snapshot={snapshot.periodResults}
          rows={results.slice(0, 8)}
          renderRow={(result: SubjectPeriodResult) => (
            <div key={result.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{result.student_name}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  average {result.final_average}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {result.subject_name} | {result.period_name}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {result.classroom_name} | {result.assessments_counted} assessments counted
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
