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
      title="Teacher Desk"
      description="Operational workspace for classroom delivery, attendance, assignments, and instructional planning."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Teacher"
              title={teacher?.name || "No teacher in scope"}
              description={teacher ? `${teacher.specialty || "General teaching"} | ${teacher.school_name || "School not resolved"}` : "Teacher scope has not been resolved from the backend yet."}
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Assignments</dt>
                <dd>{snapshot.assignments.count} learning tasks in scope.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Attendance</dt>
                <dd>{snapshot.attendance.count} classroom attendance records.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Submissions</dt>
                <dd>{snapshot.submissions.count} learner submissions visible.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Teacher secondary navigation" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Sections</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#delivery">Delivery scope</a></li>
              <li><a href="#execution">Execution and tracking</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "attendance-created" && "Attendance record created successfully."}
          {status === "attendance-error" && "Could not create the attendance record."}
          {status === "session-expired" && "Your session expired. Sign in again to continue."}
        </section>
      ) : null}

      <FilterBar
        fields={[
          {
            name: "classroom",
            label: "Classroom",
            value: classroom,
            options: Array.from(new Set(snapshot.classrooms.items.map((item) => item.name))).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "attendance_status",
            label: "Attendance",
            value: attendanceStatus,
            options: Array.from(new Set(snapshot.attendance.items.map((item) => item.status))).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "submission_status",
            label: "Submission",
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
          eyebrow="Create"
          title="Register Attendance"
          description="Quick entry form for the teacher to record presence against an enrollment."
        />
          <form action={createAttendanceAction} className="mt-3 grid gap-2 md:grid-cols-2">
            <select name="enrollment" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.enrollments.items.length > 0 ? snapshot.enrollments.items.map((enrollment) => (
                <option key={enrollment.id} value={enrollment.id}>{enrollment.student_name} | {enrollment.classroom_name}</option>
              )) : (
                <option value="">No enrollments available from current scope</option>
              )}
          </select>
          <input name="lesson_date" type="date" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <select name="status" defaultValue="present" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            <option value="present">Present</option>
            <option value="late">Late</option>
            <option value="absent">Absent</option>
            <option value="justified_absence">Justified absence</option>
          </select>
          <input name="notes" placeholder="Notes" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Save attendance" pendingLabel="Saving..." />
          </div>
        </form>
      </section>

      <section id="delivery" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Teacher Identity"
          subtitle="Current teacher record returned by the backend scope."
          snapshot={snapshot.teachers}
          rows={snapshot.teachers.items.slice(0, 3)}
          renderRow={(item: Teacher) => (
            <div key={item.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{item.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{item.school_name || "School not resolved"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{item.specialty || "No specialty registered"}</p>
            </div>
          )}
        />
        <RecordList
          title="Teaching Assignments"
          subtitle="Subjects and classrooms directly assigned to the teacher."
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
          title="Classrooms"
          subtitle="Classroom entities within the teacher's operational scope."
          snapshot={snapshot.classrooms}
          rows={snapshot.classrooms.items.slice(0, 8)}
          renderRow={(classroom: Classroom) => (
            <div key={classroom.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{classroom.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {classroom.grade_name} | {classroom.academic_year}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Lead teacher: {classroom.lead_teacher_name || "not assigned"}</p>
            </div>
          )}
        />
        <RecordList
          title="Lessons"
          subtitle="Scheduled delivery events visible to the teacher."
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
          title="Attendance Tracking"
          subtitle="Teacher-facing view of daily presence records."
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
          title="Assignments"
          subtitle="Teacher-managed learning tasks."
          snapshot={snapshot.assignments}
          rows={snapshot.assignments.items.slice(0, 8)}
          renderRow={(assignment: Assignment) => (
            <div key={assignment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{assignment.title}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{assignment.offering_title}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Due {formatDateTime(assignment.due_at)}</p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Submissions"
          subtitle="Learner work waiting for review or already graded."
          snapshot={snapshot.submissions}
          rows={filteredSubmissions.slice(0, 8)}
          renderRow={(submission: Submission) => (
            <div key={submission.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{submission.student_name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{submission.assignment_title}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {submission.status} | Score {submission.score || "pending"}
              </p>
            </div>
          )}
        />
        <RecordList
          title="Announcements"
          subtitle="Messages already published into the teacher communication flow."
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
