import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
import { formatAnnouncementAudience } from "@/lib/labels";
import {
  type Announcement,
  type Classroom,
  type Guardian,
  type StudentGuardian,
  type Teacher,
  createAnnouncement,
  getCommunicationSnapshot,
  handleMutationRedirect,
  requireAuthSession,
  updateAnnouncement,
} from "@/lib/api";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

const panelClass = "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/95 p-4 shadow-[0_18px_50px_rgba(20,33,61,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_55px_rgba(20,33,61,0.1)]";
const badgeClass = "rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70";
const controlClass = "w-full rounded-[1rem] border border-ink/10 bg-sand px-3 py-2 text-sm text-ink shadow-[inset_0_1px_0_rgba(0,0,0,0.05)] outline-none transition placeholder:text-ink/40 focus:border-ink/30 focus:ring-4 focus:ring-mist";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

// Página de comunicação: cria/edita comunicados e mostra métricas de entrega.

async function createAnnouncementAction(formData: FormData) {
  "use server";

  const school = Number(formData.get("school"));
  const classroomValue = String(formData.get("classroom") || "");
  const title = String(formData.get("title") || "").trim();
  const message = String(formData.get("message") || "").trim();
  const audience = String(formData.get("audience") || "school");

  const result = await createAnnouncement({
    school,
    classroom: classroomValue ? Number(classroomValue) : null,
    title,
    message,
    audience,
  });

  revalidatePath("/communication");
  await handleMutationRedirect(result, "/communication", "announcement-created", "announcement-error");
}

async function toggleAnnouncementAction(formData: FormData) {
  "use server";

  const id = Number(formData.get("id"));
  const active = String(formData.get("active") || "") === "true";
  const result = await updateAnnouncement(id, { active: !active });

  revalidatePath("/communication");
  await handleMutationRedirect(result, "/communication", "announcement-updated", "announcement-update-error");
}

export default async function CommunicationPage({ searchParams }: PageProps) {
  await requireAuthSession("/communication");
  const snapshot = await getCommunicationSnapshot();
  const params = (await searchParams) || {};
  const status = Array.isArray(params.status) ? params.status[0] : params.status;

  return (
    <DashboardShell
      title="Centro de comunicação"
      description="Camada de difusão e relações para turmas, professores, responsáveis e comunicados escolares."
      aside={(
        <>
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Alcance"
              title="Cobertura da audiência"
              description="Superfície de comunicação construída a partir das relações escolares e familiares."
            />
            <dl className="mt-5 space-y-4 text-sm leading-6">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Comunicados</dt>
                <dd className="text-lg font-semibold">{snapshot.announcements.count} mensagens</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Encarregados</dt>
                <dd className="text-lg font-semibold">{snapshot.guardians.count} contactos</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/75">Relações</dt>
                <dd className="text-lg font-semibold">{snapshot.studentGuardians.count} ligações</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária de comunicação" className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-white/85 p-4 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/60">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink">
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#announcements">
                  Comunicados
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#contacts">
                  Contactos e alcance
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
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Comunicação</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Navegue pela operação de comunicados e alcance familiar.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Crie mensagens, acompanhe alertas e mantenha as turmas e famílias informadas com o mesmo refinamento visual do painel executivo.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Comunicados</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.announcements.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Guardians</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.guardians.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Relações</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.studentGuardians.count}</p>
            </div>
          </div>
        </div>
      </section>
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "announcement-created" && "Comunicado criado com sucesso."}
          {status === "announcement-updated" && "Comunicado atualizado com sucesso."}
          {status === "announcement-error" && "Não foi possível criar o comunicado."}
          {status === "announcement-update-error" && "Não foi possível atualizar o comunicado."}
          {status === "session-expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <section className={panelClass}>
        <SectionTitle
          eyebrow="Criar"
          title="Publicar comunicado"
          description="Crie um novo comunicado escolar ou por turma diretamente no hub."
        />
        <form action={createAnnouncementAction} className="mt-3 grid gap-3 md:grid-cols-2">
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Escola</span>
            <select name="school" required className={controlClass}>
              {snapshot.classrooms.items
              .map((classroom) => classroom.school)
              .filter((value): value is number => value !== null)
              .filter((value, index, items) => items.indexOf(value) === index)
              .map((schoolId) => {
                const classroom = snapshot.classrooms.items.find((item) => item.school === schoolId);
                return <option key={schoolId} value={schoolId}>{classroom?.school_name || `Escola ${schoolId}`}</option>;
              })}
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Turma</span>
            <select name="classroom" className={controlClass}>
              <option value="">Toda a escola</option>
              {snapshot.classrooms.items.map((classroom) => (
                <option key={classroom.id} value={classroom.id}>{classroom.name}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Audiência</span>
            <select name="audience" defaultValue="school" className={controlClass}>
              <option value="school">Escola</option>
              <option value="classroom">Turma</option>
              <option value="teachers">Professores</option>
              <option value="guardians">Encarregados</option>
              <option value="students">Alunos</option>
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Título</span>
            <input name="title" required className={controlClass} />
          </label>
          <label className="block md:col-span-2">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Mensagem</span>
            <textarea name="message" required rows={4} className={`mt-1 w-full ${controlClass}`} />
          </label>
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Publicar comunicado" pendingLabel="A publicar..." className="w-full px-4 py-3" />
          </div>
        </form>
      </section>

      <section id="announcements" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Comunicados"
          subtitle="Mensagens para escola, turma, professores, alunos e encarregados."
          snapshot={snapshot.announcements}
          rows={snapshot.announcements.items.slice(0, 8)}
          renderRow={(announcement: Announcement) => (
            <div key={announcement.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{announcement.title}</p>
                <span className={badgeClass}>{formatAnnouncementAudience(announcement.audience)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{announcement.message}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {announcement.classroom_name || announcement.school_name || "Âmbito não definido"} · {formatDateTime(announcement.published_at)}
              </p>
              <form action={toggleAnnouncementAction} className="mt-3">
                <input type="hidden" name="id" value={announcement.id} />
                <input type="hidden" name="active" value={announcement.active ? "true" : "false"} />
                <SubmitButton
                  idleLabel={announcement.active ? "Desativar" : "Ativar"}
                  pendingLabel={announcement.active ? "A desativar..." : "A ativar..."}
                  className="w-full px-4 py-3 bg-sand text-ink border border-ink/10 hover:bg-white"
                />
              </form>
            </div>
          )}
        />
        <RecordList
          title="Ligações familiares"
          subtitle="Relações aluno-encarregado para comunicação direcionada."
          snapshot={snapshot.studentGuardians}
          rows={snapshot.studentGuardians.items.slice(0, 8)}
          renderRow={(link: StudentGuardian) => (
            <div key={link.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{link.student_name}</p>
                <span className={badgeClass}>{link.guardian_name}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                {link.primary_contact ? "Contacto principal" : "Contacto secundário"} · {link.receives_notifications ? "notificações ativas" : "notificações inativas"}
              </p>
            </div>
          )}
        />
      </section>

      <section id="contacts" className="grid gap-4 lg:grid-cols-3">
        <RecordList
          title="Encarregados"
          subtitle="Contactos familiares para escalonamento e avisos."
          snapshot={snapshot.guardians}
          rows={snapshot.guardians.items.slice(0, 6)}
          renderRow={(guardian: Guardian) => (
            <div key={guardian.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{guardian.name}</p>
                <span className={badgeClass}>{guardian.relationship || "Parentesco não definido"}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{guardian.phone || guardian.email || "Sem contacto"}</p>
            </div>
          )}
        />
        <RecordList
          title="Professores"
          subtitle="Docentes visíveis ao módulo de comunicação."
          snapshot={snapshot.teachers}
          rows={snapshot.teachers.items.slice(0, 6)}
          renderRow={(teacher: Teacher) => (
            <div key={teacher.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{teacher.name}</p>
                <span className={badgeClass}>{teacher.school_name || "Escola não identificada"}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{teacher.specialty || "Sem especialidade"}</p>
            </div>
          )}
        />
        <RecordList
          title="Turmas"
          subtitle="Grupos disponíveis para comunicação por turma."
          snapshot={snapshot.classrooms}
          rows={snapshot.classrooms.items.slice(0, 6)}
          renderRow={(classroom: Classroom) => (
            <div key={classroom.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{classroom.name}</p>
                <span className={badgeClass}>{classroom.grade_name}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{classroom.school_name}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
