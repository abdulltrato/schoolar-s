import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
import {
  type Announcement,
  type Assignment,
  type AttendanceRecord,
  type Classroom,
  type Lesson,
  type Submission,
  type Teacher,
  type TeachingAssignment,
  createAttendanceRecord,
  getTeacherPortalSnapshot,
  handleMutationRedirect,
  requireAuthSession,
} from "@/lib/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT", { dateStyle: "medium" }).format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

async function createAttendanceAction(formData: FormData) {
  "use server";

  const result = await createAttendanceRecord({
    enrollment: Number(formData.get("enrollment")),
    lesson_date: String(formData.get("lesson_date") || ""),
    status: String(formData.get("status") || "present"),
    notes: String(formData.get("notes") || "").trim(),
  });

  revalidatePath("/teacher");
  await handleMutationRedirect(result, "/teacher", "attendance-created", "attendance-error");
}

export default async function TeacherPage({ searchParams }: PageProps) {
  await requireAuthSession("/teacher");
  const snapshot = await getTeacherPortalSnapshot();
  const teacher = snapshot.teachers.items[0];
  const params = (await searchParams) || {};
  const status = Array.isArray(params.status) ? params.status[0] : params.status;
  const classroom = readParam(params.classroom);
  const attendanceStatus = readParam(params.attendance_status);
  const submissionStatus = readParam(params.submission_status);

  const filteredAssignments = snapshot.teachingAssignments.items.filter((item) => {
    if (classroom && item.classroom_name !== classroom) {
      return false;
    }
    return true;
  });

  const filteredAttendance = snapshot.attendance.items.filter((item) => {
    if (classroom && item.classroom_name !== classroom) {
      return false;
    }
    if (attendanceStatus && item.status !== attendanceStatus) {
      return false;
    }
    return true;
  });

  const filteredSubmissions = snapshot.submissions.items.filter((item) => {
    if (submissionStatus && item.status !== submissionStatus) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Painel do professor"
      description="Espaço operacional para aulas, presença, tarefas e planeamento instrucional."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Professor"
              title={teacher?.name || "Nenhum professor identificado"}
              description={teacher ? `${teacher.specialty || "Ensino geral"} | ${teacher.school_name || "Escola não identificada"}` : "O backend ainda não resolveu o escopo do professor."}
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Tarefas</dt>
                <dd>{snapshot.assignments.count} tarefas de aprendizagem no escopo.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Presença</dt>
                <dd>{snapshot.attendance.count} registos de presença.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Submissões</dt>
                <dd>{snapshot.submissions.count} submissões visíveis.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária do professor" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#delivery">Escopo de entrega</a></li>
              <li><a href="#execution">Execução e acompanhamento</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "attendance-created" && "Registo de presença criado com sucesso."}
          {status === "attendance-error" && "Não foi possível criar o registo de presença."}
          {status === "session-expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <FilterBar
        fields={[
          {
            name: "classroom",
            label: "Turma",
            value: classroom,
            options: Array.from(new Set(snapshot.classrooms.items.map((item) => item.name))).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "attendance_status",
            label: "Presença",
            value: attendanceStatus,
            options: Array.from(new Set(snapshot.attendance.items.map((item) => item.status))).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "submission_status",
            label: "Submissão",
            value: submissionStatus,
            options: Array.from(new Set(snapshot.submissions.items.map((item) => item.status))).map((item) => ({
              value: item,
              label: item,
            })),
          },
        ]}
      />

      <section className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
        <SectionTitle
          eyebrow="Criar"
          title="Registar presença"
          description="Formulário rápido para o professor registar presenças."
        />
        <form action={createAttendanceAction} className="mt-3 grid gap-2 md:grid-cols-2">
          <select name="enrollment" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            {snapshot.enrollments.items.length > 0 ? snapshot.enrollments.items.map((enrollment) => (
              <option key={enrollment.id} value={enrollment.id}>{enrollment.student_name} | {enrollment.classroom_name}</option>
            )) : (
              <option value="">Sem matrículas disponíveis no recorte atual</option>
            )}
          </select>
          <input name="lesson_date" type="date" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <select name="status" defaultValue="present" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            <option value="present">Presente</option>
            <option value="late">Atrasado</option>
            <option value="absent">Falta</option>
            <option value="justified_absence">Justificada</option>
          </select>
          <input name="notes" placeholder="Observações" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Guardar presença" pendingLabel="A guardar..." />
          </div>
        </form>
      </section>

      <section id="delivery" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Identidade do professor"
          subtitle="Registo atual do professor devolvido pelo backend."
          snapshot={snapshot.teachers}
          rows={snapshot.teachers.items.slice(0, 3)}
          renderRow={(item: Teacher) => (
            <div key={item.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{item.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{item.school_name || "Escola não identificada"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{item.specialty || "Especialidade não registada"}</p>
            </div>
          )}
        />
        <RecordList
          title="Atribuições docentes"
          subtitle="Disciplinas e turmas atribuídas ao professor."
          snapshot={snapshot.teachingAssignments}
          rows={filteredAssignments.slice(0, 8)}
          renderRow={(item: TeachingAssignment) => (
            <div key={item.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{item.subject_name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {item.classroom_name} | {item.academic_year_code}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{item.school_name}</p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Turmas"
          subtitle="Turmas dentro do escopo operacional do professor."
          snapshot={snapshot.classrooms}
          rows={snapshot.classrooms.items.slice(0, 8)}
          renderRow={(classroom: Classroom) => (
            <div key={classroom.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{classroom.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {classroom.grade_name} | {classroom.academic_year}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Diretor de turma: {classroom.lead_teacher_name || "não atribuído"}</p>
            </div>
          )}
        />
        <RecordList
          title="Aulas"
          subtitle="Eventos agendados visíveis ao professor."
          snapshot={snapshot.lessons}
          rows={snapshot.lessons.items.slice(0, 8)}
          renderRow={(lesson: Lesson) => (
            <div key={lesson.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{lesson.title}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{lesson.offering_title}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{formatDateTime(lesson.scheduled_at)}</p>
            </div>
          )}
        />
      </section>

      <section id="execution" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Acompanhamento de presença"
          subtitle="Visão do professor sobre presenças diárias."
          snapshot={snapshot.attendance}
          rows={filteredAttendance.slice(0, 8)}
          renderRow={(record: AttendanceRecord) => (
            <div key={record.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{record.student_name}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {record.status}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{record.classroom_name}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{formatDate(record.lesson_date)}</p>
            </div>
          )}
        />
        <RecordList
          title="Tarefas"
          subtitle="Tarefas geridas pelo professor."
          snapshot={snapshot.assignments}
          rows={snapshot.assignments.items.slice(0, 8)}
          renderRow={(assignment: Assignment) => (
            <div key={assignment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{assignment.title}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{assignment.offering_title}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Vencimento {formatDateTime(assignment.due_at)}</p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Submissões"
          subtitle="Trabalhos dos alunos para corrigir ou já corrigidos."
          snapshot={snapshot.submissions}
          rows={filteredSubmissions.slice(0, 8)}
          renderRow={(submission: Submission) => (
            <div key={submission.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{submission.student_name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{submission.assignment_title}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {submission.status} | Nota {submission.score ?? "por atribuir"}
              </p>
            </div>
          )}
        />
        <RecordList
          title="Comunicados"
          subtitle="Mensagens já publicadas no fluxo de comunicação do professor."
          snapshot={snapshot.announcements}
          rows={snapshot.announcements.items.slice(0, 8)}
          renderRow={(announcement: Announcement) => (
            <div key={announcement.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{announcement.title}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{announcement.message}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{announcement.audience}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
