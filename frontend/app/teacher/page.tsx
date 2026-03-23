import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
import { formatAnnouncementAudience, formatAttendanceStatus, formatSubmissionStatus } from "@/lib/labels";
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

const panelClass = "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/95 p-4 shadow-[0_18px_50px_rgba(20,33,61,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_55px_rgba(20,33,61,0.1)]";
const badgeClass = "rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70";
const controlClass = "w-full rounded-[1rem] border border-ink/10 bg-sand px-3 py-2 text-sm text-ink shadow-[inset_0_1px_0_rgba(0,0,0,0.05)] outline-none transition placeholder:text-ink/40 focus:border-ink/30 focus:ring-4 focus:ring-mist";
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
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Professor"
              title={teacher?.name || "Nenhum professor identificado"}
              description={teacher ? `${teacher.specialty || "Ensino geral"} | ${teacher.school_name || "Escola não identificada"}` : "O backend ainda não resolveu o escopo do professor."}
            />
            <dl className="mt-5 space-y-4 text-sm leading-6">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Tarefas</dt>
                <dd className="text-lg font-semibold">{snapshot.assignments.count} tarefas</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Presença</dt>
                <dd className="text-lg font-semibold">{snapshot.attendance.count} registos</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Submissões</dt>
                <dd className="text-lg font-semibold">{snapshot.submissions.count} submissões</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária do professor" className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-white/85 p-4 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/60">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink">
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#delivery">
                  Escopo de entrega
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#execution">
                  Execução e acompanhamento
                </a>
              </li>
            </ul>
          </nav>
        </>
      )}
      >
      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_55px_rgba(20,33,61,0.08)]">
        <div className="grid gap-3 sm:grid-cols-3 text-sm text-ink/70">
          <p className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">
            Turma: {classroom || "todas"}
          </p>
          <p className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">
            Presença: {attendanceStatus || "todas"}
          </p>
          <p className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">
            Submissão: {submissionStatus || "todas"}
          </p>
        </div>
      </div>
      <section className="overflow-hidden rounded-[1.5rem] border border-white/65 bg-[linear-gradient(135deg,rgba(20,33,61,0.95),rgba(32,52,85,0.95))] p-5 text-sand shadow-card shadow-[0_30px_80px_rgba(20,33,61,0.18)]">
        <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Professor</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Operação docente com visão de presença e tarefas.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Centralize planos de aula, presenças e submissões com o mesmo padrão visual que guia o resto da plataforma.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Aulas</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.lessons.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Presenças</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.attendance.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Submissões</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.submissions.count}</p>
            </div>
          </div>
        </div>
      </section>
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "attendance-created" && "Registo de presença criado com sucesso."}
          {status === "attendance-error" && "Não foi possível criar o registo de presença."}
          {status === "session-expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_55px_rgba(20,33,61,0.08)]">
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
                label: formatAttendanceStatus(item),
              })),
            },
            {
              name: "submission_status",
              label: "Submissão",
              value: submissionStatus,
              options: Array.from(new Set(snapshot.submissions.items.map((item) => item.status))).map((item) => ({
                value: item,
                label: formatSubmissionStatus(item),
              })),
            },
          ]}
        />
      </div>

      <section className={panelClass}>
        <SectionTitle
          eyebrow="Criar"
          title="Registar presença"
          description="Formulário rápido para o professor registar presenças."
        />
        <form action={createAttendanceAction} className="mt-3 grid gap-3 md:grid-cols-2">
          <select name="enrollment" required className={controlClass}>
            {snapshot.enrollments.items.length > 0 ? snapshot.enrollments.items.map((enrollment) => (
              <option key={enrollment.id} value={enrollment.id}>{enrollment.student_name} | {enrollment.classroom_name}</option>
            )) : (
              <option value="">Sem matrículas disponíveis no recorte atual</option>
            )}
          </select>
          <input name="lesson_date" type="date" required className={controlClass} />
          <select name="status" defaultValue="present" className={controlClass}>
            <option value="present">Presente</option>
            <option value="late">Atrasado</option>
            <option value="absent">Falta</option>
            <option value="justified_absence">Justificada</option>
          </select>
          <input name="notes" placeholder="Observações" className={controlClass} />
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Guardar presença" pendingLabel="A guardar..." className="w-full px-4 py-3" />
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
            <div key={item.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{item.name}</p>
                <span className={badgeClass}>{item.school_name || "Escola não identificada"}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{item.specialty || "Especialidade não registada"}</p>
            </div>
          )}
        />
        <RecordList
          title="Atribuições docentes"
          subtitle="Disciplinas e turmas atribuídas ao professor."
          snapshot={snapshot.teachingAssignments}
          rows={filteredAssignments.slice(0, 8)}
          renderRow={(item: TeachingAssignment) => (
            <div key={item.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{item.subject_name}</p>
                <span className={badgeClass}>{item.classroom_name || item.academic_year_code}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{item.school_name}</p>
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
            <div key={classroom.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{classroom.name}</p>
                <span className={badgeClass}>{classroom.grade_name}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{classroom.academic_year}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">Diretor de turma: {classroom.lead_teacher_name || "não atribuído"}</p>
            </div>
          )}
        />
        <RecordList
          title="Aulas"
          subtitle="Eventos agendados visíveis ao professor."
          snapshot={snapshot.lessons}
          rows={snapshot.lessons.items.slice(0, 8)}
          renderRow={(lesson: Lesson) => (
            <div key={lesson.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{lesson.title}</p>
                <span className={badgeClass}>{lesson.offering_title || "Oferta não identificada"}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{formatDateTime(lesson.scheduled_at)}</p>
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
            <div key={record.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{record.student_name}</p>
                <span className={badgeClass}>{formatAttendanceStatus(record.status)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{record.classroom_name}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">{formatDate(record.lesson_date)}</p>
            </div>
          )}
        />
        <RecordList
          title="Tarefas"
          subtitle="Tarefas geridas pelo professor."
          snapshot={snapshot.assignments}
          rows={snapshot.assignments.items.slice(0, 8)}
          renderRow={(assignment: Assignment) => (
            <div key={assignment.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{assignment.title}</p>
                <span className={badgeClass}>{assignment.max_score} pts</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{assignment.offering_title || "Oferta não identificada"}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">Vencimento {formatDateTime(assignment.due_at)}</p>
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
            <div key={submission.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{submission.student_name}</p>
                <span className={badgeClass}>{formatSubmissionStatus(submission.status)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{submission.assignment_title}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                Nota {submission.score ?? "por atribuir"} · {formatDateTime(submission.submitted_at || new Date().toISOString())}
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
            <div key={announcement.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{announcement.title}</p>
                <span className={badgeClass}>{formatAnnouncementAudience(announcement.audience)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{announcement.message}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
