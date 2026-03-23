import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
import { formatAnnouncementAudience, formatAttendanceStatus, formatInvoiceStatus, formatSubmissionStatus } from "@/lib/labels";
import {
  type Announcement,
  type Assignment,
  type AttendanceRecord,
  type Enrollment,
  type Invoice,
  type Lesson,
  type Student,
  type SubjectPeriodResult,
  type Submission,
  createSubmission,
  getStudentPortalSnapshot,
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
async function createSubmissionAction(formData: FormData) {
  "use server";

  const result = await createSubmission({
    assignment: Number(formData.get("assignment")),
    student: Number(formData.get("student")),
    submitted_at: new Date().toISOString(),
    text_response: String(formData.get("text_response") || "").trim(),
    attachment_url: String(formData.get("attachment_url") || "").trim(),
    status: "submitted",
  });

  revalidatePath("/student");
  await handleMutationRedirect(result, "/student", "submission-created", "submission-error");
}

export default async function StudentPage({ searchParams }: PageProps) {
  await requireAuthSession("/student");
  const snapshot = await getStudentPortalSnapshot();
  const learner = snapshot.students.items[0];
  const params = (await searchParams) || {};
  const status = Array.isArray(params.status) ? params.status[0] : params.status;
  const subject = readParam(params.subject);
  const attendanceStatus = readParam(params.attendance_status);
  const invoiceStatus = readParam(params.invoice_status);

  const filteredResults = snapshot.periodResults.items.filter((item) => {
    if (subject && item.subject_name !== subject) {
      return false;
    }
    return true;
  });

  const filteredAttendance = snapshot.attendance.items.filter((item) => {
    if (attendanceStatus && item.status !== attendanceStatus) {
      return false;
    }
    return true;
  });

  const filteredInvoices = snapshot.invoices.items.filter((item) => {
    if (invoiceStatus && item.status !== invoiceStatus) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Portal do aluno"
      description="Visão pessoal de presença, ensino em curso, resultados, comunicados e acompanhamento financeiro."
      aside={(
        <>
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Aluno"
              title={learner?.name || "Nenhum aluno identificado"}
              description={learner ? `Classe ${learner.grade} | ${learner.education_level}` : "Autenticação ou tenant ainda não resolveram um registo de aluno."}
            />
            <dl className="mt-5 space-y-4 text-sm leading-6">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Resultados</dt>
                <dd className="text-lg font-semibold">{snapshot.periodResults.count} calculados</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Presença</dt>
                <dd className="text-lg font-semibold">{snapshot.attendance.count} registos</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Faturas</dt>
                <dd className="text-lg font-semibold">{snapshot.invoices.count} pendentes</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária do aluno" className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-white/85 p-4 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/60">Secções</p>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#progress">
                  Progresso e presença
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#study">
                  Estudo e tarefas
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#money">
                  Faturas e comunicados
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
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Portal do aluno</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Controle pessoal de presença, resultados e finanças.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Informação em primeira pessoa sobre matrícula, performance, faturas e comunicados com o mesmo cuidado visual do resto da plataforma.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Resultados</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.periodResults.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Presença</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.attendance.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Finanças</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.invoices.count}</p>
            </div>
          </div>
        </div>
      </section>
      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_55px_rgba(20,33,61,0.08)]">
        <div className="grid gap-3 sm:grid-cols-3 text-sm text-ink/70">
          <p className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">
            Disciplina: {subject || "todas"}
          </p>
          <p className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">
            Presença: {attendanceStatus || "todas"}
          </p>
          <p className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">
            Fatura: {invoiceStatus || "todas"}
          </p>
        </div>
      </div>
      {status ? (
        <section className={`mt-6 rounded-[1.1rem] border px-4 py-3 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "submission-created" && "Submissão criada com sucesso."}
          {status === "submission-error" && "Não foi possível criar a submissão."}
          {status === "session-expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_55px_rgba(20,33,61,0.08)]">
        <FilterBar
          fields={[
            {
              name: "subject",
              label: "Disciplina",
              value: subject,
              options: Array.from(new Set(snapshot.periodResults.items.map((item) => item.subject_name).filter(Boolean) as string[])).map((item) => ({
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
              name: "invoice_status",
              label: "Fatura",
              value: invoiceStatus,
              options: Array.from(new Set(snapshot.invoices.items.map((item) => item.status))).map((item) => ({
                value: item,
                label: formatInvoiceStatus(item),
              })),
            },
          ]}
        />
      </div>

      <section id="progress" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Matrícula"
          subtitle="Posição atual do aluno na turma."
          snapshot={snapshot.enrollments}
          rows={snapshot.enrollments.items.slice(0, 4)}
          renderRow={(enrollment: Enrollment) => (
            <div key={enrollment.id} className={panelClass}>
              <p className="font-semibold text-ink">{enrollment.classroom_name}</p>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {enrollment.school_name} · {enrollment.academic_year_code}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">Matriculado em {formatDate(enrollment.enrollment_date)}</p>
            </div>
          )}
        />
        <RecordList
          title="Resultados por disciplina"
          subtitle="Médias ponderadas por período já calculadas."
          snapshot={snapshot.periodResults}
          rows={filteredResults.slice(0, 8)}
          renderRow={(result: SubjectPeriodResult) => (
            <div key={result.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{result.subject_name}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  {result.final_average}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{result.period_name}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">{result.assessments_counted} avaliações contabilizadas</p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Presenças"
          subtitle="Histórico de presença no recorte ativo."
          snapshot={snapshot.attendance}
          rows={filteredAttendance.slice(0, 8)}
          renderRow={(record: AttendanceRecord) => (
            <div key={record.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{record.classroom_name}</p>
                <span className={badgeClass}>{formatAttendanceStatus(record.status)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{formatDate(record.lesson_date)}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">{record.notes || "Sem observações de presença."}</p>
            </div>
          )}
        />
        <RecordList
          title="Aulas futuras"
          subtitle="Agenda de aprendizagem visível ao aluno."
          snapshot={snapshot.lessons}
          rows={snapshot.lessons.items.slice(0, 8)}
          renderRow={(lesson: Lesson) => (
            <div key={lesson.id} className={panelClass}>
              <p className="font-semibold text-ink">{lesson.title}</p>
              <p className="mt-2 text-sm leading-6 text-ink/70">{lesson.offering_title}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">{formatDateTime(lesson.scheduled_at)}</p>
            </div>
          )}
        />
      </section>

      <section className={panelClass}>
        <SectionTitle
          eyebrow="Enviar"
          title="Enviar tarefa"
          description="Submeta texto ou um link para uma tarefa disponível."
        />
        <form action={createSubmissionAction} className="mt-3 grid gap-3 md:grid-cols-2">
          <input type="hidden" name="student" value={learner?.id || ""} />
          <select name="assignment" required className={controlClass}>
            {snapshot.assignments.items.map((assignment) => (
              <option key={assignment.id} value={assignment.id}>{assignment.title}</option>
            ))}
          </select>
          <input name="attachment_url" type="url" placeholder="URL do anexo" className={controlClass} />
          <label className="block md:col-span-2">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Resposta</span>
            <textarea name="text_response" rows={4} className={`mt-1 w-full ${controlClass}`} />
          </label>
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Enviar" pendingLabel="A enviar..." className="w-full px-4 py-3" />
          </div>
        </form>
      </section>

      <section id="study" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Tarefas"
          subtitle="Tarefas abertas e prazos do aluno."
          snapshot={snapshot.assignments}
          rows={snapshot.assignments.items.slice(0, 8)}
          renderRow={(assignment: Assignment) => (
            <div key={assignment.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{assignment.title}</p>
                <span className="rounded-full bg-ember/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ember">
                  {assignment.max_score} pts
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{assignment.offering_title}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">Vencimento {formatDateTime(assignment.due_at)}</p>
            </div>
          )}
        />
        <RecordList
          title="Submissões"
          subtitle="O que o aluno já entregou pela plataforma."
          snapshot={snapshot.submissions}
          rows={snapshot.submissions.items.slice(0, 8)}
          renderRow={(submission: Submission) => (
            <div key={submission.id} className={panelClass}>
              <p className="font-semibold text-ink">{submission.assignment_title}</p>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {submission.submitted_at ? formatDateTime(submission.submitted_at) : "Ainda não submetido"}
              </p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                Estado: {formatSubmissionStatus(submission.status)} | Nota: {submission.score ?? "por atribuir"}
              </p>
            </div>
          )}
        />
      </section>

      <section id="money" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Faturas"
          subtitle="Acompanhamento financeiro para aluno/responsável."
          snapshot={snapshot.invoices}
          rows={filteredInvoices.slice(0, 8)}
          renderRow={(invoice: Invoice) => (
            <div key={invoice.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{invoice.reference}</p>
                <span className={badgeClass}>{formatInvoiceStatus(invoice.status)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{invoice.description}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                Montante {invoice.amount} · Vencimento {formatDate(invoice.due_date)}
              </p>
            </div>
          )}
        />
        <RecordList
          title="Comunicados"
          subtitle="Comunicações escolares visíveis ao aluno."
          snapshot={snapshot.announcements}
          rows={snapshot.announcements.items.slice(0, 8)}
          renderRow={(announcement: Announcement) => (
            <div key={announcement.id} className={panelClass}>
              <p className="font-semibold text-ink">{announcement.title}</p>
              <p className="mt-2 text-sm leading-6 text-ink/70">{announcement.message}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {formatAnnouncementAudience(announcement.audience)} · {formatDateTime(announcement.published_at)}
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
