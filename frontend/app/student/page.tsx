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
      title="Student Portal"
      description="Personal view of attendance, active learning, results, school notices, and financial follow-up."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Student"
              title={learner?.name || "No learner in scope"}
              description={learner ? `Grade ${learner.grade} | ${learner.education_level}` : "Authentication or tenant scope has not resolved a student record yet."}
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Results</dt>
                <dd>{snapshot.periodResults.count} calculated subject results.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Attendance</dt>
                <dd>{snapshot.attendance.count} attendance records in scope.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Invoices</dt>
                <dd>{snapshot.invoices.count} financial records available.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Student secondary navigation" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Sections</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#progress">Progress and attendance</a></li>
              <li><a href="#study">Study plan and tasks</a></li>
              <li><a href="#money">Invoices and notices</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "submission-created" && "Submission created successfully."}
          {status === "submission-error" && "Could not create the submission."}
          {status === "session-expired" && "Your session expired. Sign in again to continue."}
        </section>
      ) : null}

      <FilterBar
        fields={[
          {
            name: "subject",
            label: "Subject",
            value: subject,
            options: Array.from(new Set(snapshot.periodResults.items.map((item) => item.subject_name).filter(Boolean) as string[])).map((item) => ({
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
            name: "invoice_status",
            label: "Invoice",
            value: invoiceStatus,
            options: Array.from(new Set(snapshot.invoices.items.map((item) => item.status))).map((item) => ({
              value: item,
              label: item,
            })),
          },
        ]}
      />

      <section id="progress" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Enrollment"
          subtitle="Current classroom placement for the student in scope."
          snapshot={snapshot.enrollments}
          rows={snapshot.enrollments.items.slice(0, 4)}
          renderRow={(enrollment: Enrollment) => (
            <div key={enrollment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{enrollment.classroom_name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {enrollment.school_name} | {enrollment.academic_year_code}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Enrolled on {formatDate(enrollment.enrollment_date)}</p>
            </div>
          )}
        />
        <RecordList
          title="Subject Results"
          subtitle="Period-based weighted averages already calculated by the backend."
          snapshot={snapshot.periodResults}
          rows={filteredResults.slice(0, 8)}
          renderRow={(result: SubjectPeriodResult) => (
            <div key={result.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{result.subject_name}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  {result.final_average}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{result.period_name}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{result.assessments_counted} assessments counted</p>
            </div>
          )}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Attendance"
          subtitle="Presence history for the learner in the active scope."
          snapshot={snapshot.attendance}
          rows={filteredAttendance.slice(0, 8)}
          renderRow={(record: AttendanceRecord) => (
            <div key={record.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{record.classroom_name}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {record.status}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{formatDate(record.lesson_date)}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{record.notes || "No attendance notes."}</p>
            </div>
          )}
        />
        <RecordList
          title="Upcoming Lessons"
          subtitle="Learning agenda visible to the student."
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

      <section className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
        <SectionTitle
          eyebrow="Submit"
          title="Send Assignment Work"
          description="Submit text or an attachment URL for an available assignment."
        />
        <form action={createSubmissionAction} className="mt-3 grid gap-2 md:grid-cols-2">
          <input type="hidden" name="student" value={learner?.id || ""} />
          <select name="assignment" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
            {snapshot.assignments.items.map((assignment) => (
              <option key={assignment.id} value={assignment.id}>{assignment.title}</option>
            ))}
          </select>
          <input name="attachment_url" type="url" placeholder="Attachment URL" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          <label className="block md:col-span-2">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Text Response</span>
            <textarea name="text_response" rows={4} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
          </label>
          <div className="md:col-span-2">
            <SubmitButton idleLabel="Submit work" pendingLabel="Submitting..." />
          </div>
        </form>
      </section>

      <section id="study" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Assignments"
          subtitle="Open tasks and deadlines for the student."
          snapshot={snapshot.assignments}
          rows={snapshot.assignments.items.slice(0, 8)}
          renderRow={(assignment: Assignment) => (
            <div key={assignment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{assignment.title}</p>
                <span className="rounded-full bg-ember/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ember">
                  {assignment.max_score} pts
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{assignment.offering_title}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Due {formatDateTime(assignment.due_at)}</p>
            </div>
          )}
        />
        <RecordList
          title="Submissions"
          subtitle="What the student has already delivered through the platform."
          snapshot={snapshot.submissions}
          rows={snapshot.submissions.items.slice(0, 8)}
          renderRow={(submission: Submission) => (
            <div key={submission.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{submission.assignment_title}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {submission.submitted_at ? formatDateTime(submission.submitted_at) : "Not submitted yet"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Status: {submission.status} | Score: {submission.score || "pending"}
              </p>
            </div>
          )}
        />
      </section>

      <section id="money" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Invoices"
          subtitle="Financial follow-up for the student or guardian portal."
          snapshot={snapshot.invoices}
          rows={filteredInvoices.slice(0, 8)}
          renderRow={(invoice: Invoice) => (
            <div key={invoice.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{invoice.reference}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {invoice.status}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{invoice.description}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                Amount {invoice.amount} | Due {formatDate(invoice.due_date)}
              </p>
            </div>
          )}
        />
        <RecordList
          title="Announcements"
          subtitle="School communications visible inside the student experience."
          snapshot={snapshot.announcements}
          rows={snapshot.announcements.items.slice(0, 8)}
          renderRow={(announcement: Announcement) => (
            <div key={announcement.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{announcement.title}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{announcement.message}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {announcement.audience} | {formatDateTime(announcement.published_at)}
              </p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
