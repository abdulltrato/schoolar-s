import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import {
  type Classroom,
  type Enrollment,
  type ManagementAssignment,
  type School,
  getManagementSnapshot,
  requireAuthSession,
} from "@/lib/api";
import {
  countClassroomsBySchool,
  countEnrollmentsByClassroom,
  describeAssignmentScope,
  filterClassrooms,
  filterEnrollments,
  filterManagementAssignments,
  formatRole,
  readParam,
} from "./filters";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

const panelClass = "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/95 p-4 shadow-[0_18px_45px_rgba(20,33,61,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_25px_60px_rgba(20,33,61,0.15)]";
const secondaryBadge = "rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70";

export default async function ManagementPage({ searchParams }: PageProps) {
  await requireAuthSession("/management");
  const snapshot = await getManagementSnapshot();
  const params = (await searchParams) || {};
  const filters = {
    school: readParam(params.school),
    year: readParam(params.year),
    role: readParam(params.role),
  };
  const classrooms = filterClassrooms(snapshot, filters);
  const enrollments = filterEnrollments(snapshot, filters);
  const assignments = filterManagementAssignments(snapshot, filters);

  return (
    <DashboardShell
      title="Gestão escolar"
      description="Visão institucional de escolas, turmas, matrículas e cargos de gestão."
      aside={(
        <>
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Resumo"
              title="Âmbito atual"
              description="Referências rápidas para o recorte operacional desta página."
            />
            <dl className="mt-5 space-y-4 text-sm leading-6 text-sand/80">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Escolas</dt>
                <dd className="text-lg font-semibold">{snapshot.schools.count} registadas</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Turmas</dt>
                <dd className="text-lg font-semibold">{classrooms.length} visíveis</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Matrículas</dt>
                <dd className="text-lg font-semibold">{enrollments.length} filtradas</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária da gestão" className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-white/80 p-5 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/60">Secções</p>
            <ul className="mt-4 grid gap-2 text-sm font-medium text-ink">
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#schools">
                  Escolas e cargos
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#classrooms">
                  Turmas e matrículas
                </a>
              </li>
            </ul>
          </nav>
        </>
      )}
    >
      <section className="overflow-hidden rounded-[1.5rem] border border-white/70 bg-[linear-gradient(135deg,rgba(20,33,61,0.95),rgba(32,52,85,0.95))] p-5 text-sand shadow-card shadow-[0_30px_80px_rgba(20,33,61,0.18)]">
        <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr] lg:items-end">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Gestão</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Controle completo das unidades escolares e cargos de liderança.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Consulte o mapa de escolas ativas, cargos de coordenação e turmas vinculadas. Os filtros mantêm o contexto operacional para qualquer recorte de ano letivo, escola ou função.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Escolas</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.schools.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Cargos</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.managementAssignments.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Turmas</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.classrooms.count}</p>
            </div>
          </div>
        </div>
      </section>

      <div className="mt-6 rounded-[1.25rem] border border-white/30 bg-white/70 p-4 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
        <div className="grid gap-3 text-sm text-ink/70 sm:grid-cols-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/45">Filtro atual</p>
            <p className="mt-1 text-[13px] text-ink/80">
              Escola: {filters.school || "Todas"} · Ano: {filters.year || "Todos"} · Cargo: {filters.role || "Todos"}
            </p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/45">Turmas filtradas</p>
            <p className="mt-1 font-display text-2xl font-semibold text-ink">{classrooms.length}</p>
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/45">Matrículas filtradas</p>
            <p className="mt-1 font-display text-2xl font-semibold text-ink">{enrollments.length}</p>
          </div>
        </div>
      </div>

      <FilterBar
        fields={[
          {
            name: "school",
            label: "Escola",
            value: filters.school,
            options: snapshot.schools.items.map((item) => ({
              value: String(item.id),
              label: item.name,
            })),
          },
          {
            name: "year",
            label: "Ano letivo",
            value: filters.year,
            options: snapshot.academicYears.items.map((item) => ({
              value: item.code,
              label: item.code,
            })),
          },
          {
            name: "role",
            label: "Cargo",
            value: filters.role,
            options: Array.from(new Set(snapshot.managementAssignments.items.map((item) => item.role))).map((item) => ({
              value: item,
              label: formatRole(item),
            })),
          },
        ]}
      />

      <section id="schools" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Escolas"
          subtitle="Base institucional da plataforma."
          snapshot={snapshot.schools}
          rows={snapshot.schools.items.slice(0, 6)}
          renderRow={(school: School) => {
            const classroomCount = countClassroomsBySchool(snapshot.classrooms.items, school.id);

            return (
              <div key={school.id} className={panelClass}>
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{school.name}</p>
                  <span className={secondaryBadge}>
                    {school.active ? "ativa" : "inativa"}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  {school.code} | {school.district || "distrito não definido"} | {school.province || "província não definida"}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">{classroomCount} turmas ligadas a esta escola.</p>
              </div>
            );
          }}
        />

        <RecordList
          title="Cargos de gestão"
          subtitle="Liderança e coordenação por ano letivo e âmbito."
          snapshot={snapshot.managementAssignments}
          rows={assignments.slice(0, 8)}
          renderRow={(assignment: ManagementAssignment) => (
            <div key={assignment.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{assignment.teacher_name}</p>
                <span className={secondaryBadge}>
                  {assignment.academic_year_code}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {formatRole(assignment.role)} em {assignment.school_name}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {describeAssignmentScope(assignment)}
              </p>
            </div>
          )}
        />
      </section>

      <section id="classrooms" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Turmas"
          subtitle="Turmas ligadas à escola, classe, ano letivo e diretor de turma."
          snapshot={snapshot.classrooms}
          rows={classrooms.slice(0, 8)}
          renderRow={(classroom: Classroom) => {
            const enrollmentCount = countEnrollmentsByClassroom(snapshot.enrollments.items, classroom.id);

            return (
              <div key={classroom.id} className={panelClass}>
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{classroom.name}</p>
                  <span className={secondaryBadge}>
                    {enrollmentCount} matrículas
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  {classroom.school_name} | {classroom.academic_year} | {classroom.grade_name}
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">
                  Diretor de turma: {classroom.lead_teacher_name || "não atribuído"}
                </p>
              </div>
            );
          }}
        />

        <RecordList
          title="Matrículas"
          subtitle="Distribuição de alunos pelas turmas da escola."
          snapshot={snapshot.enrollments}
          rows={enrollments.slice(0, 8)}
          renderRow={(enrollment: Enrollment) => (
            <div key={enrollment.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{enrollment.student_name}</p>
                <span className={secondaryBadge}>
                  {enrollment.academic_year_code}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {enrollment.school_name} | {enrollment.classroom_name}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">Classe {enrollment.grade_number}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
