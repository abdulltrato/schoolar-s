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

const panelClass = "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/95 p-4 shadow-[0_18px_50px_rgba(20,33,61,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_55px_rgba(20,33,61,0.1)]";
const badgeClass = "rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70";
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
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Resumo"
              title="Abrangência curricular"
              description="Indicadores compactos do recorte curricular ativo."
            />
            <dl className="mt-5 space-y-4 text-sm leading-6">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Disciplinas</dt>
                <dd className="text-lg font-semibold">{offerings.length} visíveis</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Planos</dt>
                <dd className="text-lg font-semibold">{plans.length} carregados</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Classes</dt>
                <dd className="text-lg font-semibold">{snapshot.grades.count} níveis</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária do currículo" className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-white/85 p-4 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/60">Secções</p>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#offerings">
                  Oferta de disciplinas
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#plans">
                  Planos curriculares
                </a>
              </li>
            </ul>
          </nav>
        </>
      )}
    >
      <section className="overflow-hidden rounded-[1.5rem] border border-white/65 bg-[linear-gradient(135deg,rgba(20,33,61,0.95),rgba(32,52,85,0.95))] p-5 text-sand shadow-card shadow-[0_30px_80px_rgba(20,33,61,0.18)]">
        <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Currículo</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Oferta de disciplinas guiada por planos e ciclos letivos.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Ajuste o recorte para ano letivo ou classe e veja os planos associados a cada disciplina com metas e metodologias.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Disciplinas</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.gradeSubjects.items.length}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Planos</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.subjectPlans.items.length}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Níveis</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.grades.count}</p>
            </div>
          </div>
        </div>
      </section>
      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_55px_rgba(20,33,61,0.08)]">
        <p className="text-sm text-ink/70">
          Recorte atual — ano: {year || "todos"} · classe: {grade || "todas"}.
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
          <div key={subject.id} className={panelClass}>
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-ink">{subject.subject_name}</p>
              <span className={badgeClass}>{subject.academic_year}</span>
            </div>
            <p className="mt-2 text-sm leading-6 text-ink/70">Classe {subject.grade}</p>
            <p className="mt-1 text-sm leading-6 text-ink/55">Carga horária semanal: {subject.weekly_workload}</p>
          </div>
          )}
        />

        <RecordList
          title="Planos curriculares"
          subtitle="Objetivos, metodologia e critérios de avaliação por disciplina."
          snapshot={snapshot.subjectPlans}
          rows={plans.slice(0, 8)}
          renderRow={(plan: SubjectCurriculumPlan) => (
          <div key={plan.id} className={panelClass}>
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-ink">{plan.subject_name}</p>
              <span className={badgeClass}>{plan.academic_year_code}</span>
            </div>
            <p className="mt-2 text-sm leading-6 text-ink/70">
              Classe {plan.grade_number} · {plan.planned_competencies.length} competências
            </p>
            <p className="mt-1 text-sm leading-6 text-ink/55">
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
