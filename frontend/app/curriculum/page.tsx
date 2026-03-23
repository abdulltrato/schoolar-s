import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import {
  type GradeSubject,
  type SubjectCurriculumPlan,
  getCurriculumSnapshot,
} from "@/lib/api";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(
  value: string | string[] | undefined,
) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export default async function CurriculumPage({ searchParams }: PageProps) {
  const snapshot = await getCurriculumSnapshot();
  const params = (await searchParams) || {};
  const year = readParam(params.year);
  const grade = readParam(params.grade);

  const offerings = snapshot.gradeSubjects.items.filter((item) => {
    if (year && item.academic_year !== year) {
      return false;
    }
    if (grade && String(item.grade) !== grade) {
      return false;
    }
    return true;
  });

  const plans = snapshot.subjectPlans.items.filter((item) => {
    if (year && item.academic_year_code !== year) {
      return false;
    }
    if (grade && String(item.grade_number) !== grade) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Curriculum"
      description="Subject offerings by grade and academic year, with formal curriculum plans per subject."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Summary"
              title="Curriculum Coverage"
              description="Compact indicators for the active curriculum slice."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Offerings</dt>
                <dd>{offerings.length} subjects in the current filter.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Plans</dt>
                <dd>{plans.length} visible curriculum plans.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Grades</dt>
                <dd>{snapshot.grades.count} registered levels.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Curriculum secondary navigation" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Sections</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#offerings">Subject offerings</a></li>
              <li><a href="#plans">Curriculum plans</a></li>
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
            name: "grade",
            label: "Grade",
            value: grade,
            options: snapshot.grades.items.map((item) => ({
              value: String(item.number),
              label: item.name,
            })),
          },
        ]}
      />

      <section id="offerings" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Subject Offerings"
          subtitle="Subjects configured by grade and academic year."
          snapshot={snapshot.gradeSubjects}
          rows={offerings.slice(0, 8)}
          renderRow={(subject: GradeSubject) => (
            <div key={subject.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{subject.subject_name}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {subject.academic_year}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">Grade {subject.grade}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Weekly workload: {subject.weekly_workload}
              </p>
            </div>
          )}
        />

        <RecordList
          title="Curriculum Plans"
          subtitle="Objectives, methodology, and assessment criteria by subject."
          snapshot={snapshot.subjectPlans}
          rows={plans.slice(0, 8)}
          renderRow={(plan: SubjectCurriculumPlan) => (
            <div key={plan.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{plan.subject_name}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {plan.academic_year_code}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                Grade {plan.grade_number} | {plan.planned_competencies.length} competencies
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {plan.assessment_criteria || plan.methodology || plan.objectives || "No narrative detail has been filled in yet."}
              </p>
            </div>
          )}
        />
      </section>
      <section id="plans" className="sr-only" aria-hidden="true" />
    </DashboardShell>
  );
}
