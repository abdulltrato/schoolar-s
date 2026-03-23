import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import {
  type GradeSubject,
  type SubjectCurriculumPlan,
  getCurriculumSnapshot,
  requireAuthSession,
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
  await requireAuthSession("/curriculum");
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
      title="Currículo"
      description="Oferta de disciplinas por classe e ano letivo, com planos formais por disciplina."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Resumo"
              title="Abrangência curricular"
              description="Indicadores compactos do recorte curricular ativo."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Disciplinas</dt>
                <dd>{offerings.length} disciplinas com o filtro atual.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Planos</dt>
                <dd>{plans.length} planos curriculares visíveis.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Classes</dt>
                <dd>{snapshot.grades.count} níveis registados.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária do currículo" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#offerings">Oferta de disciplinas</a></li>
              <li><a href="#plans">Planos curriculares</a></li>
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
            name: "grade",
            label: "Classe",
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
          title="Oferta de disciplinas"
          subtitle="Disciplinas configuradas por classe e ano letivo."
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
              <p className="mt-1.5 text-sm leading-5 text-ink/70">Classe {subject.grade}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Carga horária semanal: {subject.weekly_workload}
              </p>
            </div>
          )}
        />

        <RecordList
          title="Planos curriculares"
          subtitle="Objetivos, metodologia e critérios de avaliação por disciplina."
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
                Classe {plan.grade_number} | {plan.planned_competencies.length} competências
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {plan.assessment_criteria || plan.methodology || plan.objectives || "Ainda não foram preenchidos detalhes narrativos."}
              </p>
            </div>
          )}
        />
      </section>
      <section id="plans" className="sr-only" aria-hidden="true" />
    </DashboardShell>
  );
}
