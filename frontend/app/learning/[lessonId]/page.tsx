import Link from "next/link";
import { notFound } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { SectionTitle } from "@/components/section-title";
import { formatCourseModality, formatMaterialType, formatPublishedState } from "@/lib/labels";
import {
  type Lesson,
  type LessonMaterial,
  type CourseOffering,
  getLearningSnapshot,
  requireAuthSession,
} from "@/lib/api";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "long",
    timeStyle: "short",
  }).format(new Date(value));
}

function findLesson(id: number, lessons: Lesson[]): Lesson | undefined {
  return lessons.find((lesson) => lesson.id === id);
}

function materialsForLesson(id: number, materials: LessonMaterial[]) {
  return materials.filter((material) => material.lesson === id);
}

function offeringForLesson(lesson: Lesson, offerings: CourseOffering[]) {
  return offerings.find((item) => item.id === lesson.offering);
}

function modalityForOffering(offering?: CourseOffering, courses?: { id: number; modality: string }[]) {
  if (!offering || !courses) return "";
  return courses.find((c) => c.id === offering.course)?.modality || "";
}

type PageProps = {
  params: Promise<{ lessonId: string }>;
};

export default async function LessonDetailPage({ params }: PageProps) {
  const resolvedParams = await params;
  await requireAuthSession(`/learning/${resolvedParams.lessonId}`);
  const snapshot = await getLearningSnapshot();
  const lessonId = Number(resolvedParams.lessonId);
  const lesson = findLesson(lessonId, snapshot.lessons.items);
  if (!lesson) {
    notFound();
  }
  const lessonMaterials = materialsForLesson(lessonId, snapshot.materials.items);
  const offering = offeringForLesson(lesson, snapshot.offerings.items);
  const modality = modalityForOffering(offering, snapshot.courses.items);

  return (
    <DashboardShell
      title="Aula"
      description="Detalhe da sessão, links e materiais associados."
      aside={(
        <section className="rounded-[1.1rem] border border-ink/10 bg-sand p-4">
          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Acesso rápido</p>
          <ul className="mt-3 space-y-2 text-sm text-ink/75">
            <li><a href="#info">Informação</a></li>
            <li><a href="#materials">Materiais</a></li>
          </ul>
        </section>
      )}
    >
      <section id="info" className="overflow-hidden rounded-[1.3rem] border border-white/70 bg-white/95 p-5 shadow-[0_22px_60px_rgba(20,33,61,0.08)]">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-fern/80">Aula</p>
            <h1 className="mt-1 font-display text-3xl font-bold text-ink">{lesson.title}</h1>
            <p className="mt-2 text-sm leading-6 text-ink/70">{lesson.description || "Sem descrição."}</p>
            <Link href="/learning" className="mt-2 inline-block text-xs font-semibold text-fern hover:underline">
              Voltar para ensino
            </Link>
          </div>
          <div className="flex gap-2">
            <span className="rounded-full bg-mist px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
              {formatPublishedState(lesson.published)}
            </span>
            {offering ? (
              <span className="rounded-full bg-ink/90 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-white">
                {offering.academic_year_code}
              </span>
            ) : null}
          </div>
        </div>
        <dl className="mt-4 grid gap-4 text-sm text-ink/75 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-[1rem] border border-ink/10 bg-ink/4 p-3">
            <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Data</dt>
            <dd className="mt-1 font-semibold text-ink">{formatDateTime(lesson.scheduled_at)}</dd>
            <p className="text-xs text-ink/55">{lesson.duration_minutes} minutos</p>
          </div>
          <div className="rounded-[1rem] border border-ink/10 bg-ink/4 p-3">
            <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Oferta</dt>
            <dd className="mt-1 font-semibold text-ink">{lesson.offering_title || "Oferta não identificada"}</dd>
            <p className="text-xs text-ink/55">{offering?.teacher_name || "Professor não definido"}</p>
          </div>
          {offering ? (
            <div className="rounded-[1rem] border border-ink/10 bg-ink/4 p-3">
              <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Modalidade</dt>
              <dd className="mt-1 font-semibold text-ink">{modality ? formatCourseModality(modality) : "Não definido"}</dd>
              <p className="text-xs text-ink/55">{offering.classroom_name || "Turma não definida"}</p>
            </div>
          ) : null}
        </dl>

        <div className="mt-4 flex flex-wrap gap-2">
          {lesson.meeting_url ? (
            <a
              href={lesson.meeting_url}
              className="rounded-full border border-ink/10 bg-fern/90 px-4 py-2 text-sm font-semibold text-white transition hover:bg-fern/80"
            >
              Entrar na sessão
            </a>
          ) : null}
          {lesson.recording_url ? (
            <a
              href={lesson.recording_url}
              className="rounded-full border border-ink/10 bg-ink px-4 py-2 text-sm font-semibold text-white transition hover:bg-ink/90"
            >
              Rever gravação
            </a>
          ) : null}
        </div>
      </section>

      <section id="materials" className="rounded-[1.3rem] border border-white/70 bg-white/95 p-5 shadow-[0_22px_60px_rgba(20,33,61,0.08)]">
        <SectionTitle
          eyebrow="Materiais"
          title="Recursos desta aula"
          description="PDFs, links, vídeos e outros recursos ligados à sessão."
        />
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {lessonMaterials.length === 0 ? (
            <p className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 text-sm text-ink/70">Nenhum material anexado.</p>
          ) : lessonMaterials.map((material) => (
            <div key={material.id} className="rounded-[1rem] border border-ink/10 bg-sand px-4 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{material.title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {formatMaterialType(material.material_type)}
                </span>
              </div>
              <p className="mt-1 text-xs text-ink/60">{material.required ? "Obrigatório" : "Opcional"}</p>
              <a
                className="mt-2 inline-block text-sm font-semibold text-fern hover:underline"
                href={material.url}
                target="_blank"
                rel="noreferrer"
              >
                Abrir recurso
              </a>
            </div>
          ))}
        </div>
      </section>
    </DashboardShell>
  );
}
