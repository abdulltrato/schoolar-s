import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
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

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

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
      title="Hub de comunicação"
      description="Camada de difusão e relações para turmas, professores, responsáveis e comunicados escolares."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Alcance"
              title="Cobertura da audiência"
              description="Superfície de comunicação construída a partir das relações escolares e familiares."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Comunicados</dt>
                <dd>{snapshot.announcements.count} mensagens disponíveis.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Encarregados</dt>
                <dd>{snapshot.guardians.count} contactos familiares no escopo.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Ligações</dt>
                <dd>{snapshot.studentGuardians.count} relações aluno-família mapeadas.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária de comunicação" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#announcements">Comunicados</a></li>
              <li><a href="#contacts">Contactos e alcance</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "announcement-created" && "Comunicado criado com sucesso."}
          {status === "announcement-updated" && "Comunicado atualizado com sucesso."}
          {status === "announcement-error" && "Não foi possível criar o comunicado."}
          {status === "announcement-update-error" && "Não foi possível atualizar o comunicado."}
          {status === "session-expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <section className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
        <SectionTitle
          eyebrow="Criar"
          title="Publicar comunicado"
          description="Crie um novo comunicado escolar ou por turma diretamente no hub."
        />
        <form action={createAnnouncementAction} className="mt-3 grid gap-2 md:grid-cols-2">
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Escola</span>
            <select name="school" required className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
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
            <select name="classroom" className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Toda a escola</option>
              {snapshot.classrooms.items.map((classroom) => (
                <option key={classroom.id} value={classroom.id}>{classroom.name}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Audiência</span>
            <select name="audience" defaultValue="school" className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="school">Escola</option>
              <option value="classroom">Turma</option>
              <option value="teachers">Professores</option>
              <option value="guardians">Encarregados</option>
              <option value="students">Alunos</option>
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Título</span>
            <input name="title" required className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          </label>
          <label className="block md:col-span-2">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Mensagem</span>
            <textarea name="message" required rows={4} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          </label>
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Publicar comunicado" pendingLabel="A publicar..." />
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
            <div key={announcement.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{announcement.title}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{announcement.message}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {announcement.audience} | {announcement.classroom_name || announcement.school_name || "Âmbito não definido"} | {formatDateTime(announcement.published_at)}
              </p>
              <form action={toggleAnnouncementAction} className="mt-2">
                <input type="hidden" name="id" value={announcement.id} />
                <input type="hidden" name="active" value={announcement.active ? "true" : "false"} />
                <button type="submit" className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink">
                  {announcement.active ? "Desativar" : "Ativar"}
                </button>
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
            <div key={link.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{link.student_name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{link.guardian_name}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {link.primary_contact ? "Contacto principal" : "Contacto secundário"} | {link.receives_notifications ? "notificações ativas" : "notificações inativas"}
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
            <div key={guardian.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{guardian.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{guardian.relationship || "Parentesco não definido"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{guardian.phone || guardian.email || "Sem contacto"}</p>
            </div>
          )}
        />
        <RecordList
          title="Professores"
          subtitle="Docentes visíveis ao módulo de comunicação."
          snapshot={snapshot.teachers}
          rows={snapshot.teachers.items.slice(0, 6)}
          renderRow={(teacher: Teacher) => (
            <div key={teacher.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{teacher.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{teacher.school_name}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{teacher.specialty || "Sem especialidade"}</p>
            </div>
          )}
        />
        <RecordList
          title="Turmas"
          subtitle="Grupos disponíveis para comunicação por turma."
          snapshot={snapshot.classrooms}
          rows={snapshot.classrooms.items.slice(0, 6)}
          renderRow={(classroom: Classroom) => (
            <div key={classroom.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{classroom.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{classroom.grade_name}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{classroom.school_name}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
