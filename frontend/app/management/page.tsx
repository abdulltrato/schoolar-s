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
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Resumo"
              title="Âmbito atual"
              description="Referências rápidas para o recorte operacional desta página."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Escolas</dt>
                <dd>{snapshot.schools.count} unidades registadas.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Turmas</dt>
                <dd>{classrooms.length} turmas no recorte atual.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Matrículas</dt>
                <dd>{enrollments.length} alunos filtrados pelos critérios ativos.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária da gestão" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#schools">Escolas e cargos</a></li>
              <li><a href="#classrooms">Turmas e matrículas</a></li>
            </ul>
          </nav>
        </>
      )}
    >
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
              <div key={school.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{school.name}</p>
                  <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                    {school.active ? "ativa" : "inativa"}
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-5 text-ink/70">
                  {school.code} | {school.district || "distrito não definido"} | {school.province || "província não definida"}
                </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">{classroomCount} turmas ligadas a esta escola.</p>
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
            <div key={assignment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{assignment.teacher_name}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {assignment.academic_year_code}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {formatRole(assignment.role)} em {assignment.school_name}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
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
              <div key={classroom.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-ink">{classroom.name}</p>
                  <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                    {enrollmentCount} matrículas
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-5 text-ink/70">
                  {classroom.school_name} | {classroom.academic_year} | {classroom.grade_name}
                </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">
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
            <div key={enrollment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{enrollment.student_name}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {enrollment.academic_year_code}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {enrollment.school_name} | {enrollment.classroom_name}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Classe {enrollment.grade_number}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
