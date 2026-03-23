import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
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
      title="Learning Operations"
      description="Digital delivery layer for courses, live lessons, materials, assignments, and submissions."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Coverage"
              title="Learning Surface"
              description="Operational summary of the online and blended teaching stack."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Courses</dt>
                <dd>{snapshot.courses.count} configured learning products.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Lessons</dt>
                <dd>{snapshot.lessons.count} lessons loaded from the backend.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Assignments</dt>
                <dd>{snapshot.assignments.count} published or draft tasks.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Learning secondary navigation" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Sections</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#courses">Courses and delivery</a></li>
              <li><a href="#work">Assignments and submissions</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "lesson-created" && "Lesson created successfully."}
          {status === "assignment-created" && "Assignment created successfully."}
          {status === "material-created" && "Lesson material created successfully."}
          {status === "lesson-updated" && "Lesson updated successfully."}
          {status === "assignment-updated" && "Assignment updated successfully."}
          {status === "lesson-error" && "Could not create the lesson."}
          {status === "assignment-error" && "Could not create the assignment."}
          {status === "material-error" && "Could not create the lesson material."}
          {status === "lesson-update-error" && "Could not update the lesson."}
          {status === "assignment-update-error" && "Could not update the assignment."}
          {status === "session-expired" && "Your session expired. Sign in again to continue."}
        </section>
      ) : null}

      <FilterBar
        fields={[
          {
            name: "modality",
            label: "Modality",
            value: modality,
            options: Array.from(new Set(snapshot.courses.items.map((item) => item.modality))).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "teacher",
            label: "Teacher",
            value: teacher,
            options: Array.from(new Set(snapshot.offerings.items.map((item) => item.teacher_name).filter(Boolean) as string[])).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "published",
            label: "Published",
            value: published,
            options: [
              { value: "true", label: "Published" },
              { value: "false", label: "Draft" },
            ],
          },
        ]}
      />

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Create"
            title="Schedule Lesson"
            description="Open a new teaching event from the learning operations workspace."
          />
          <form action={createLessonAction} className="mt-3 grid gap-2">
            <select name="offering" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.offerings.items.map((offering) => (
                <option key={offering.id} value={offering.id}>{offering.course_title} | {offering.classroom_name || "No classroom"}</option>
              ))}
            </select>
            <input name="title" required placeholder="Lesson title" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <textarea name="description" rows={3} placeholder="Lesson description" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="scheduled_at" type="datetime-local" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="duration_minutes" type="number" min="1" defaultValue="45" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="meeting_url" type="url" placeholder="Meeting URL" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <label className="flex items-center gap-2 text-sm text-ink/75">
              <input name="published" type="checkbox" />
              Publish immediately
            </label>
            <SubmitButton idleLabel="Create lesson" pendingLabel="Creating lesson..." />
          </form>
        </article>

        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Create"
            title="Open Assignment"
            description="Publish a new task with opening and due windows."
          />
          <form action={createAssignmentAction} className="mt-3 grid gap-2">
            <select name="offering" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.offerings.items.map((offering) => (
                <option key={offering.id} value={offering.id}>{offering.course_title} | {offering.classroom_name || "No classroom"}</option>
              ))}
            </select>
            <input name="title" required placeholder="Assignment title" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <textarea name="instructions" rows={3} placeholder="Instructions" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="opens_at" type="datetime-local" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="due_at" type="datetime-local" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="max_score" type="number" min="1" defaultValue="20" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <label className="flex items-center gap-2 text-sm text-ink/75">
              <input name="published" type="checkbox" />
              Publish immediately
            </label>
            <SubmitButton idleLabel="Create assignment" pendingLabel="Creating assignment..." />
          </form>
        </article>
      </section>

      <section className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
        <SectionTitle
          eyebrow="Create"
          title="Attach Lesson Material"
          description="Add a link, document, video, or another resource to an existing lesson."
        />
        <form action={createLessonMaterialAction} className="mt-3 grid gap-2 md:grid-cols-2">
          <select name="lesson" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            {snapshot.lessons.items.map((lesson) => (
              <option key={lesson.id} value={lesson.id}>{lesson.title}</option>
            ))}
          </select>
          <input name="title" required placeholder="Material title" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <select name="material_type" defaultValue="document" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            <option value="link">Link</option>
            <option value="document">Document</option>
            <option value="video">Video</option>
            <option value="audio">Audio</option>
            <option value="other">Other</option>
          </select>
          <input name="url" type="url" required placeholder="Resource URL" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <label className="flex items-center gap-2 text-sm text-ink/75 md:col-span-2">
            <input name="required" type="checkbox" />
            Mark as required material
          </label>
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Attach material" pendingLabel="Attaching material..." />
          </div>
        </form>
      </section>

      <section id="courses" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Courses"
          subtitle="Configured online, blended, and classroom-supported learning products."
          snapshot={snapshot.courses}
          rows={filteredCourses.slice(0, 6)}
          renderRow={(course: Course) => (
            <div key={course.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{course.title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {course.modality}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{course.school_name || "School not resolved"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {course.description || "No course description has been filled in yet."}
              </p>
            </div>
          )}
        />
        <RecordList
          title="Offerings"
          subtitle="Operational delivery by teacher, classroom, and academic year."
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
                {offering.teacher_name || "Teacher not assigned"} | {offering.classroom_name || "No classroom"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {offering.start_date} to {offering.end_date}
              </p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Lessons"
          subtitle="Scheduled delivery with optional meeting and recording links."
          snapshot={snapshot.lessons}
          rows={filteredLessons.slice(0, 8)}
          renderRow={(lesson: Lesson) => (
            <div key={lesson.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{lesson.title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {lesson.published ? "published" : "draft"}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {lesson.offering_title || "Offering not resolved"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {formatDateTime(lesson.scheduled_at)} | {lesson.duration_minutes} min
              </p>
              <form action={toggleLessonPublicationAction} className="mt-2">
                <input type="hidden" name="id" value={lesson.id} />
                <input type="hidden" name="published" value={lesson.published ? "true" : "false"} />
                <button type="submit" className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink">
                  {lesson.published ? "Unpublish" : "Publish"}
                </button>
              </form>
            </div>
          )}
        />
        <RecordList
          title="Materials"
          subtitle="Learning assets attached to lesson execution."
          snapshot={snapshot.materials}
          rows={snapshot.materials.items.slice(0, 8)}
          renderRow={(material: LessonMaterial) => (
            <div key={material.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{material.title}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {material.material_type}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{material.lesson_title || "Lesson not resolved"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {material.required ? "Required material" : "Optional material"}
              </p>
            </div>
          )}
        />
      </section>

      <section id="work" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Assignments"
          subtitle="Task windows with publication and due-date controls."
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
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{assignment.offering_title || "Offering not resolved"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Opens {formatDateTime(assignment.opens_at)} | Due {formatDateTime(assignment.due_at)}
              </p>
              <form action={toggleAssignmentPublicationAction} className="mt-2">
                <input type="hidden" name="id" value={assignment.id} />
                <input type="hidden" name="published" value={assignment.published ? "true" : "false"} />
                <button type="submit" className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink">
                  {assignment.published ? "Unpublish" : "Publish"}
                </button>
              </form>
            </div>
          )}
        />
        <RecordList
          title="Submissions"
          subtitle="Learner work returned through the digital learning flow."
          snapshot={snapshot.submissions}
          rows={snapshot.submissions.items.slice(0, 8)}
          renderRow={(submission: Submission) => (
            <div key={submission.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{submission.student_name || "Student not resolved"}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  {submission.status}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{submission.assignment_title || "Assignment not resolved"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Score: {submission.score || "not graded"} | Submitted: {submission.submitted_at ? formatDateTime(submission.submitted_at) : "pending"}
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
