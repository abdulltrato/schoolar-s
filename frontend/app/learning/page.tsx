import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
import { formatCourseModality, formatMaterialType, formatPublishedState, formatSubmissionStatus } from "@/lib/labels";
import {
  type Assignment,
  type Course,
  type CourseOffering,
  type Lesson,
  type LessonMaterial,
  type Submission,
  createAssignment,
  createLesson,
  createLessonMaterial,
  getLearningSnapshot,
  handleMutationRedirect,
  requireAuthSession,
  updateAssignment,
  updateLesson,
} from "@/lib/api";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

async function createLessonAction(formData: FormData) {
  "use server";

  const result = await createLesson({
    offering: Number(formData.get("offering")),
    title: String(formData.get("title") || "").trim(),
    description: String(formData.get("description") || "").trim(),
    scheduled_at: String(formData.get("scheduled_at") || ""),
    duration_minutes: Number(formData.get("duration_minutes") || 45),
    meeting_url: String(formData.get("meeting_url") || "").trim(),
    recording_url: String(formData.get("recording_url") || "").trim(),
    published: String(formData.get("published") || "") === "on",
  });

  revalidatePath("/learning");
  await handleMutationRedirect(result, "/learning", "lesson-created", "lesson-error");
}

async function createAssignmentAction(formData: FormData) {
  "use server";

  const result = await createAssignment({
    offering: Number(formData.get("offering")),
    title: String(formData.get("title") || "").trim(),
    instructions: String(formData.get("instructions") || "").trim(),
    opens_at: String(formData.get("opens_at") || ""),
    due_at: String(formData.get("due_at") || ""),
    max_score: Number(formData.get("max_score") || 20),
    published: String(formData.get("published") || "") === "on",
  });

  revalidatePath("/learning");
  await handleMutationRedirect(result, "/learning", "assignment-created", "assignment-error");
}

async function createLessonMaterialAction(formData: FormData) {
  "use server";

  const result = await createLessonMaterial({
    lesson: Number(formData.get("lesson")),
    title: String(formData.get("title") || "").trim(),
    material_type: String(formData.get("material_type") || "document"),
    url: String(formData.get("url") || "").trim(),
    required: String(formData.get("required") || "") === "on",
  });

  revalidatePath("/learning");
  await handleMutationRedirect(result, "/learning", "material-created", "material-error");
}

async function toggleLessonPublicationAction(formData: FormData) {
  "use server";

  const id = Number(formData.get("id"));
  const published = String(formData.get("published") || "") === "true";
  const result = await updateLesson(id, { published: !published });

  revalidatePath("/learning");
  await handleMutationRedirect(result, "/learning", "lesson-updated", "lesson-update-error");
}

async function toggleAssignmentPublicationAction(formData: FormData) {
  "use server";

  const id = Number(formData.get("id"));
  const published = String(formData.get("published") || "") === "true";
  const result = await updateAssignment(id, { published: !published });

  revalidatePath("/learning");
  await handleMutationRedirect(result, "/learning", "assignment-updated", "assignment-update-error");
}

export default async function LearningPage({ searchParams }: PageProps) {
  await requireAuthSession("/learning");
  const snapshot = await getLearningSnapshot();
  const params = (await searchParams) || {};
  const status = Array.isArray(params.status) ? params.status[0] : params.status;
  const modality = readParam(params.modality);
  const teacher = readParam(params.teacher);
  const published = readParam(params.published);

  const filteredCourses = snapshot.courses.items.filter((course) => {
    if (modality && course.modality !== modality) {
      return false;
    }
    return true;
  });

  const filteredOfferings = snapshot.offerings.items.filter((offering) => {
    if (teacher && offering.teacher_name !== teacher) {
      return false;
    }
    return true;
  });

  const filteredLessons = snapshot.lessons.items.filter((lesson) => {
    if (published && String(lesson.published) !== published) {
      return false;
    }
    return true;
  });

  const filteredAssignments = snapshot.assignments.items.filter((assignment) => {
    if (published && String(assignment.published) !== published) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Operações de ensino"
      description="Camada digital para cursos, aulas, materiais, tarefas e submissões."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Cobertura"
              title="Superfície de ensino"
              description="Resumo operacional dos fluxos presenciais, híbridos e online."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Cursos</dt>
                <dd>{snapshot.courses.count} produtos de ensino configurados.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Aulas</dt>
                <dd>{snapshot.lessons.count} aulas carregadas do backend.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Tarefas</dt>
                <dd>{snapshot.assignments.count} tarefas publicadas ou rascunho.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária de ensino" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#courses">Cursos e ofertas</a></li>
              <li><a href="#work">Tarefas e submissões</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "lesson-created" && "Aula criada com sucesso."}
          {status === "assignment-created" && "Tarefa criada com sucesso."}
          {status === "material-created" && "Material da aula criado com sucesso."}
          {status === "lesson-updated" && "Aula atualizada com sucesso."}
          {status === "assignment-updated" && "Tarefa atualizada com sucesso."}
          {status === "lesson-error" && "Não foi possível criar a aula."}
          {status === "assignment-error" && "Não foi possível criar a tarefa."}
          {status === "material-error" && "Não foi possível criar o material."}
          {status === "lesson-update-error" && "Não foi possível atualizar a aula."}
          {status === "assignment-update-error" && "Não foi possível atualizar a tarefa."}
          {status === "session-expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <FilterBar
        fields={[
          {
            name: "modality",
            label: "Modalidade",
            value: modality,
            options: Array.from(new Set(snapshot.courses.items.map((item) => item.modality))).map((item) => ({
              value: item,
              label: formatCourseModality(item),
            })),
          },
          {
            name: "teacher",
            label: "Professor",
            value: teacher,
            options: Array.from(new Set(snapshot.offerings.items.map((item) => item.teacher_name).filter(Boolean) as string[])).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "published",
            label: "Publicado",
            value: published,
            options: [
              { value: "true", label: "Publicado" },
              { value: "false", label: "Rascunho" },
            ],
          },
        ]}
      />

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Criar"
            title="Agendar aula"
            description="Abra um novo evento letivo a partir da área de operações de ensino."
          />
          <form action={createLessonAction} className="mt-3 grid gap-2">
            <select name="offering" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.offerings.items.map((offering) => (
                <option key={offering.id} value={offering.id}>{offering.course_title} | {offering.classroom_name || "Turma não definida"}</option>
              ))}
            </select>
            <input name="title" required placeholder="Título da aula" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <textarea name="description" rows={3} placeholder="Descrição da aula" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="scheduled_at" type="datetime-local" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="duration_minutes" type="number" min="1" defaultValue="45" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="meeting_url" type="url" placeholder="URL da aula" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <label className="flex items-center gap-2 text-sm text-ink/75">
              <input name="published" type="checkbox" />
              Publicar imediatamente
            </label>
            <SubmitButton idleLabel="Criar aula" pendingLabel="A criar aula..." />
          </form>
        </article>

        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Criar"
            title="Abrir tarefa"
            description="Publique uma nova tarefa com janela de abertura e vencimento."
          />
          <form action={createAssignmentAction} className="mt-3 grid gap-2">
            <select name="offering" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.offerings.items.map((offering) => (
                <option key={offering.id} value={offering.id}>{offering.course_title} | {offering.classroom_name || "Turma não definida"}</option>
              ))}
            </select>
            <input name="title" required placeholder="Título da tarefa" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <textarea name="instructions" rows={3} placeholder="Instruções" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="opens_at" type="datetime-local" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="due_at" type="datetime-local" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="max_score" type="number" min="1" defaultValue="20" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <label className="flex items-center gap-2 text-sm text-ink/75">
              <input name="published" type="checkbox" />
              Publicar imediatamente
            </label>
            <SubmitButton idleLabel="Criar tarefa" pendingLabel="A criar tarefa..." />
          </form>
        </article>
      </section>

      <section className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
        <SectionTitle
          eyebrow="Criar"
          title="Adicionar material"
          description="Anexe link, documento, vídeo ou outro recurso a uma aula existente."
        />
        <form action={createLessonMaterialAction} className="mt-3 grid gap-2 md:grid-cols-2">
          <select name="lesson" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            {snapshot.lessons.items.map((lesson) => (
              <option key={lesson.id} value={lesson.id}>{lesson.title}</option>
            ))}
          </select>
          <input name="title" required placeholder="Título do material" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <select name="material_type" defaultValue="document" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            <option value="link">Link</option>
            <option value="document">Documento</option>
            <option value="video">Vídeo</option>
            <option value="audio">Áudio</option>
            <option value="other">Outro</option>
          </select>
          <input name="url" type="url" required placeholder="URL do recurso" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <label className="flex items-center gap-2 text-sm text-ink/75 md:col-span-2">
            <input name="required" type="checkbox" />
            Marcar como material obrigatório
          </label>
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Anexar material" pendingLabel="A anexar material..." />
          </div>
        </form>
      </section>

      <section id="courses" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Cursos"
          subtitle="Produtos de ensino online, híbrido e presencial já configurados."
          snapshot={snapshot.courses}
          rows={filteredCourses.slice(0, 6)}
          renderRow={(course: Course) => (
            <div key={course.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{course.title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {formatCourseModality(course.modality)}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{course.school_name || "Escola não identificada"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {course.description || "Ainda não existe descrição preenchida para este curso."}
              </p>
            </div>
          )}
        />
        <RecordList
          title="Ofertas"
          subtitle="Execução operacional por professor, turma e ano letivo."
          snapshot={snapshot.offerings}
          rows={filteredOfferings.slice(0, 6)}
          renderRow={(offering: CourseOffering) => (
            <div key={offering.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{offering.course_title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {offering.academic_year_code}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {offering.teacher_name || "Professor não atribuído"} | {offering.classroom_name || "Turma não definida"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {offering.start_date} a {offering.end_date}
              </p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Aulas"
          subtitle="Execução agendada com links opcionais de sessão e gravação."
          snapshot={snapshot.lessons}
          rows={filteredLessons.slice(0, 8)}
          renderRow={(lesson: Lesson) => (
            <div key={lesson.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{lesson.title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {formatPublishedState(lesson.published)}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {lesson.offering_title || "Oferta não identificada"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {formatDateTime(lesson.scheduled_at)} | {lesson.duration_minutes} min
              </p>
              <form action={toggleLessonPublicationAction} className="mt-2">
                <input type="hidden" name="id" value={lesson.id} />
                <input type="hidden" name="published" value={lesson.published ? "true" : "false"} />
                <button type="submit" className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink">
                  {lesson.published ? "Retirar publicação" : "Publicar"}
                </button>
              </form>
            </div>
          )}
        />
        <RecordList
          title="Materiais"
          subtitle="Recursos de aprendizagem associados à execução da aula."
          snapshot={snapshot.materials}
          rows={snapshot.materials.items.slice(0, 8)}
          renderRow={(material: LessonMaterial) => (
            <div key={material.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{material.title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {formatMaterialType(material.material_type)}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{material.lesson_title || "Aula não identificada"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {material.required ? "Material obrigatório" : "Material opcional"}
              </p>
            </div>
          )}
        />
      </section>

      <section id="work" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Tarefas"
          subtitle="Janelas de trabalho com controlo de publicação e vencimento."
          snapshot={snapshot.assignments}
          rows={filteredAssignments.slice(0, 8)}
          renderRow={(assignment: Assignment) => (
            <div key={assignment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{assignment.title}</p>
                <span className="rounded-full bg-ember/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ember">
                  {assignment.max_score} pts
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{assignment.offering_title || "Oferta não identificada"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Abre {formatDateTime(assignment.opens_at)} | Vence {formatDateTime(assignment.due_at)}
              </p>
              <form action={toggleAssignmentPublicationAction} className="mt-2">
                <input type="hidden" name="id" value={assignment.id} />
                <input type="hidden" name="published" value={assignment.published ? "true" : "false"} />
                <button type="submit" className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink">
                  {assignment.published ? "Retirar publicação" : "Publicar"}
                </button>
              </form>
            </div>
          )}
        />
        <RecordList
          title="Submissões"
          subtitle="Trabalho devolvido pelos alunos através do fluxo digital."
          snapshot={snapshot.submissions}
          rows={snapshot.submissions.items.slice(0, 8)}
          renderRow={(submission: Submission) => (
            <div key={submission.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{submission.student_name || "Aluno não identificado"}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  {formatSubmissionStatus(submission.status)}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{submission.assignment_title || "Tarefa não identificada"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Nota: {submission.score ?? "por corrigir"} | Submetido: {submission.submitted_at ? formatDateTime(submission.submitted_at) : "pendente"}
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
