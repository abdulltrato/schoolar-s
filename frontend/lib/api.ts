import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { apiPath, resolveApiBaseUrl } from "@/lib/api-path";

type HealthPayload = {
  status?: string;
};

type ReadinessPayload = {
  status?: string;
  checks?: Record<string, string>;
};

type PaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

export type StudentCompetency = {
  id: number;
  code: string;
  competency: number;
  competency_name: string;
  level: string;
  updated_at: string;
};

export type Student = {
  id: number;
  code: string;
  user: number | null;
  name: string;
  tenant_id: string;
  birth_date: string;
  grade: number;
  cycle: number;
  education_level: string;
  status: string;
  competencies: StudentCompetency[];
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
};

export type AcademicYear = {
  id: number;
  code: string;
  start_date: string;
  end_date: string;
  active: boolean;
};

export type Grade = {
  id: number;
  code: string;
  number: number;
  cycle: number;
  education_level: string;
  name: string;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
};

export type School = {
  id: number;
  code: string;
  name: string;
  district: string;
  province: string;
  active: boolean;
};

export type Teacher = {
  id: number;
  user: number;
  tenant_id: string;
  school: number | null;
  school_name?: string;
  name: string;
  specialty: string;
};

export type Classroom = {
  id: number;
  name: string;
  tenant_id: string;
  school: number | null;
  school_name?: string;
  grade: number;
  grade_name?: string;
  cycle: number;
  academic_year: string;
  lead_teacher: number | null;
  lead_teacher_name?: string;
};

export type GradeSubject = {
  id: number;
  academic_year: string;
  grade: number;
  subject: number;
  subject_name?: string;
  weekly_workload: number;
};

export type TeachingAssignment = {
  id: number;
  teacher: number;
  tenant_id?: string;
  teacher_name?: string;
  classroom: number;
  classroom_name?: string;
  school_name?: string;
  grade_subject: number;
  subject_name?: string;
  academic_year_code?: string;
  grade_number?: number;
};

export type Enrollment = {
  id: number;
  student: number;
  tenant_id?: string;
  student_name?: string;
  classroom: number;
  classroom_name?: string;
  enrollment_date: string;
  school_name?: string;
  academic_year_code?: string;
  grade_number?: number;
};

export type ManagementAssignment = {
  id: number;
  teacher: number;
  teacher_name?: string;
  school: number;
  school_name?: string;
  academic_year: number;
  academic_year_code?: string;
  role: string;
  grade: number | null;
  grade_number?: number;
  classroom: number | null;
  classroom_name?: string;
  cycle: number | null;
  active: boolean;
};

export type SubjectCurriculumPlan = {
  id: number;
  grade_subject: number;
  subject_name?: string;
  grade_number?: number;
  academic_year_code?: string;
  objectives: string;
  methodology: string;
  assessment_criteria: string;
  active: boolean;
  planned_competencies: Array<{ id: number; name: string }>;
};

export type AssessmentPeriod = {
  id: number;
  academic_year: number;
  academic_year_code?: string;
  name: string;
  order: number;
  start_date: string;
  end_date: string;
  active: boolean;
};

export type AssessmentComponent = {
  id: number;
  period: number;
  period_name?: string;
  grade_subject: number;
  subject_name?: string;
  grade_number?: number;
  academic_year_code?: string;
  type: string;
  name: string;
  weight: string;
  max_score: string;
  mandatory: boolean;
};

export type Assessment = {
  id: number;
  student: number;
  tenant_id?: string;
  student_name?: string;
  teaching_assignment: number | null;
  period: number | null;
  period_name?: string;
  component: number | null;
  component_name?: string;
  competency: number | null;
  competency_name?: string;
  teacher_name?: string;
  classroom_name?: string;
  subject_name?: string;
  academic_year_code?: string;
  grade_number?: number;
  type: string;
  date: string;
  score: string | null;
  comment: string;
  knowledge: boolean;
  skills: boolean;
  attitudes: boolean;
};

export type SubjectPeriodResult = {
  id: number;
  student: number;
  student_name?: string;
  teaching_assignment: number;
  teacher_name?: string;
  classroom_name?: string;
  subject_name?: string;
  period: number;
  period_name?: string;
  final_average: string;
  assessments_counted: number;
};

export type Guardian = {
  id: number;
  user: number | null;
  tenant_id: string;
  name: string;
  phone: string;
  email: string;
  relationship: string;
  active: boolean;
};

export type StudentGuardian = {
  id: number;
  student: number;
  student_name?: string;
  guardian: number;
  guardian_name?: string;
  primary_contact: boolean;
  receives_notifications: boolean;
};

export type AttendanceRecord = {
  id: number;
  enrollment: number;
  tenant_id: string;
  student_name?: string;
  classroom_name?: string;
  lesson_date: string;
  status: string;
  notes: string;
};

export type Announcement = {
  id: number;
  school: number;
  classroom: number | null;
  author: number | null;
  tenant_id: string;
  school_name?: string;
  classroom_name?: string;
  author_name?: string;
  title: string;
  message: string;
  audience: string;
  published_at: string;
  active: boolean;
};

export type Invoice = {
  id: number;
  student: number;
  school: number;
  tenant_id: string;
  student_name?: string;
  school_name?: string;
  reference: string;
  description: string;
  amount: string;
  due_date: string;
  status: string;
  issued_at: string;
};

export type Payment = {
  id: number;
  invoice: number;
  tenant_id: string;
  invoice_reference?: string;
  amount: string;
  payment_date: string;
  method: string;
  reference: string;
  notes: string;
};

export type AuditEvent = {
  id: number;
  resource: string;
  action: string;
  object_id: number;
  object_repr: string;
  tenant_id: string;
  request_id: string;
  path: string;
  method: string;
  role: string;
  username: string;
  changed_fields: string[];
  created_at: string;
};

export type AuditAlert = {
  id: number;
  alert_type: string;
  severity: string;
  tenant_id: string;
  resource: string;
  username: string;
  summary: string;
  details: Record<string, unknown>;
  acknowledged: boolean;
  created_at: string;
};

export type Course = {
  id: number;
  school: number;
  tenant_id: string;
  school_name?: string;
  title: string;
  description: string;
  modality: string;
  active: boolean;
};

export type CourseOffering = {
  id: number;
  course: number;
  classroom: number | null;
  teacher: number | null;
  academic_year: number;
  tenant_id: string;
  course_title?: string;
  classroom_name?: string;
  teacher_name?: string;
  academic_year_code?: string;
  start_date: string;
  end_date: string;
  active: boolean;
};

export type Lesson = {
  id: number;
  offering: number;
  tenant_id: string;
  offering_title?: string;
  title: string;
  description: string;
  scheduled_at: string;
  duration_minutes: number;
  meeting_url: string;
  recording_url: string;
  published: boolean;
};

export type LessonMaterial = {
  id: number;
  lesson: number;
  lesson_title?: string;
  title: string;
  material_type: string;
  url: string;
  required: boolean;
};

export type Assignment = {
  id: number;
  offering: number;
  tenant_id: string;
  offering_title?: string;
  title: string;
  instructions: string;
  opens_at: string;
  due_at: string;
  max_score: string;
  published: boolean;
};

export type Submission = {
  id: number;
  assignment: number;
  student: number;
  tenant_id: string;
  assignment_title?: string;
  student_name?: string;
  submitted_at: string | null;
  text_response: string;
  attachment_url: string;
  score: string | null;
  feedback: string;
  status: string;
};

type EndpointSnapshot = {
  ok: boolean;
  status: string;
  message: string;
};

export type CollectionSnapshot<T> = {
  ok: boolean;
  status: string;
  statusCode: number;
  count: number;
  items: T[];
  next: string | null;
  previous: string | null;
  message: string;
  requiresAuth: boolean;
};

type PlatformMeta = {
  baseUrlLabel: string;
  authConfigured: boolean;
  tenantId: string | null;
  health: EndpointSnapshot;
  readiness: EndpointSnapshot;
};

export type AuthUser = {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
  role: string | null;
  tenant_id: string;
  school_id: number | null;
  active?: boolean;
};

type AuthPayload = {
  ok?: boolean;
  user?: AuthUser;
  error?: {
    code?: string;
    message?: string;
  };
};

export type HomeSnapshot = PlatformMeta & {
  schools: CollectionSnapshot<School>;
  managementAssignments: CollectionSnapshot<ManagementAssignment>;
  subjectPlans: CollectionSnapshot<SubjectCurriculumPlan>;
  periods: CollectionSnapshot<AssessmentPeriod>;
  components: CollectionSnapshot<AssessmentComponent>;
  periodResults: CollectionSnapshot<SubjectPeriodResult>;
};

export type ManagementSnapshot = PlatformMeta & {
  academicYears: CollectionSnapshot<AcademicYear>;
  schools: CollectionSnapshot<School>;
  classrooms: CollectionSnapshot<Classroom>;
  enrollments: CollectionSnapshot<Enrollment>;
  managementAssignments: CollectionSnapshot<ManagementAssignment>;
};

export type CurriculumSnapshot = PlatformMeta & {
  academicYears: CollectionSnapshot<AcademicYear>;
  grades: CollectionSnapshot<Grade>;
  gradeSubjects: CollectionSnapshot<GradeSubject>;
  subjectPlans: CollectionSnapshot<SubjectCurriculumPlan>;
};

export type AssessmentSnapshot = PlatformMeta & {
  academicYears: CollectionSnapshot<AcademicYear>;
  classrooms: CollectionSnapshot<Classroom>;
  periods: CollectionSnapshot<AssessmentPeriod>;
  components: CollectionSnapshot<AssessmentComponent>;
  assessments: CollectionSnapshot<Assessment>;
  periodResults: CollectionSnapshot<SubjectPeriodResult>;
};

export type StudentPortalSnapshot = PlatformMeta & {
  students: CollectionSnapshot<Student>;
  enrollments: CollectionSnapshot<Enrollment>;
  attendance: CollectionSnapshot<AttendanceRecord>;
  assessments: CollectionSnapshot<Assessment>;
  periodResults: CollectionSnapshot<SubjectPeriodResult>;
  invoices: CollectionSnapshot<Invoice>;
  announcements: CollectionSnapshot<Announcement>;
  courses: CollectionSnapshot<Course>;
  lessons: CollectionSnapshot<Lesson>;
  assignments: CollectionSnapshot<Assignment>;
  submissions: CollectionSnapshot<Submission>;
};

export type TeacherPortalSnapshot = PlatformMeta & {
  teachers: CollectionSnapshot<Teacher>;
  classrooms: CollectionSnapshot<Classroom>;
  enrollments: CollectionSnapshot<Enrollment>;
  teachingAssignments: CollectionSnapshot<TeachingAssignment>;
  attendance: CollectionSnapshot<AttendanceRecord>;
  assessments: CollectionSnapshot<Assessment>;
  announcements: CollectionSnapshot<Announcement>;
  offerings: CollectionSnapshot<CourseOffering>;
  lessons: CollectionSnapshot<Lesson>;
  assignments: CollectionSnapshot<Assignment>;
  submissions: CollectionSnapshot<Submission>;
};

export type FinanceSnapshot = PlatformMeta & {
  schools: CollectionSnapshot<School>;
  students: CollectionSnapshot<Student>;
  guardians: CollectionSnapshot<Guardian>;
  invoices: CollectionSnapshot<Invoice>;
  payments: CollectionSnapshot<Payment>;
};

export type CommunicationSnapshot = PlatformMeta & {
  announcements: CollectionSnapshot<Announcement>;
  guardians: CollectionSnapshot<Guardian>;
  studentGuardians: CollectionSnapshot<StudentGuardian>;
  classrooms: CollectionSnapshot<Classroom>;
  teachers: CollectionSnapshot<Teacher>;
};

export type LearningSnapshot = PlatformMeta & {
  courses: CollectionSnapshot<Course>;
  offerings: CollectionSnapshot<CourseOffering>;
  lessons: CollectionSnapshot<Lesson>;
  materials: CollectionSnapshot<LessonMaterial>;
  assignments: CollectionSnapshot<Assignment>;
  submissions: CollectionSnapshot<Submission>;
};

export type AuditSnapshot = PlatformMeta & {
  auditEvents: CollectionSnapshot<AuditEvent>;
  auditAlerts: CollectionSnapshot<AuditAlert>;
};

export type ReportRecord = {
  id: number;
  title: string;
  type: string;
  generated_at: string;
  period: string;
  content: Record<string, unknown>;
  student: number | null;
  verification_code: string;
  verification_hash: string;
  verification_version: number;
  verification_url: string;
  verification_status: string;
};

export type ReportCatalogItem = {
  key: string;
  label: string;
  scope: string;
  requires: string[];
};

export type GeneratedReportPayload = {
  title?: string;
  report_kind: string;
  generated_at: string;
  generated_by?: string | null;
  scope: string;
  metadata?: Record<string, unknown>;
  student_snapshot?: Record<string, unknown>;
  summary?: Record<string, unknown>;
  rows?: Array<Record<string, unknown>>;
};

export type ReportsSnapshot = PlatformMeta & {
  reports: CollectionSnapshot<ReportRecord>;
  catalog: CollectionSnapshot<ReportCatalogItem>;
  students: CollectionSnapshot<Student>;
  academicYears: CollectionSnapshot<AcademicYear>;
  grades: CollectionSnapshot<Grade>;
  classrooms: CollectionSnapshot<Classroom>;
  teachers: CollectionSnapshot<Teacher>;
  managementAssignments: CollectionSnapshot<ManagementAssignment>;
};

export type ReportVerification = {
  valid: boolean;
  reason: string;
  verification_code: string;
  verification_hash: string;
  report_id: number;
  title: string;
  type: string;
  period: string;
  generated_at: string;
  student_name?: string | null;
  verification_version: number;
};

function resolveTenantId() {
  return process.env.API_TENANT_ID || process.env.NEXT_PUBLIC_TENANT_ID || null;
}

async function resolveCookieAuthHeader() {
  try {
    const cookieStore = await cookies();
    const sessionId = cookieStore.get("schoolar_sessionid")?.value;
    const csrfToken = cookieStore.get("schoolar_csrftoken")?.value;
    if (sessionId) {
      return {
        cookieHeader: [`sessionid=${sessionId}`, csrfToken ? `csrftoken=${csrfToken}` : ""]
          .filter(Boolean)
          .join("; "),
        csrfToken: csrfToken || null,
        authMode: "session" as const,
      };
    }
  } catch {
    return null;
  }

  return null;
}

function resolveBasicAuthHeaderFromEnv() {
  const username = process.env.API_USERNAME;
  const password = process.env.API_PASSWORD;

  if (!username || !password) {
    return null;
  }

  return `Basic ${Buffer.from(`${username}:${password}`).toString("base64")}`;
}

async function resolveAuthContext() {
  const cookieAuth = await resolveCookieAuthHeader();
  if (cookieAuth) {
    return cookieAuth;
  }

  const basicAuthHeader = resolveBasicAuthHeaderFromEnv();
  if (basicAuthHeader) {
    return {
      authorizationHeader: basicAuthHeader,
      csrfToken: null,
      authMode: "basic" as const,
    };
  }

  return {
    csrfToken: null,
    authMode: "none" as const,
  };
}

async function buildHeaders(method: "GET" | "POST" | "PATCH" = "GET") {
  const headers = new Headers({
    Accept: "application/json",
  });

  const authContext = await resolveAuthContext();
  const tenantId = resolveTenantId();

  if ("authorizationHeader" in authContext && authContext.authorizationHeader) {
    headers.set("Authorization", authContext.authorizationHeader);
  }

  if ("cookieHeader" in authContext && authContext.cookieHeader) {
    headers.set("Cookie", authContext.cookieHeader);
  }

  if (method !== "GET" && authContext.csrfToken) {
    headers.set("X-CSRFToken", authContext.csrfToken);
  }

  if (tenantId) {
    headers.set("X-Tenant-ID", tenantId);
  }

  return headers;
}

async function parseJsonSafe<T>(response: Response): Promise<T | undefined> {
  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    return undefined;
  }

  try {
    return (await response.json()) as T;
  } catch {
    return undefined;
  }
}

async function readJson<T>(path: string): Promise<{ ok: boolean; statusCode: number; data?: T }> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      cache: "no-store",
      headers: await buildHeaders("GET"),
    });

    const data = await parseJsonSafe<T>(response);
    return { ok: response.ok, statusCode: response.status, data };
  } catch {
    return { ok: false, statusCode: 0 };
  }
}

type MutationResult<T> = {
  ok: boolean;
  statusCode: number;
  data?: T;
  error?: string;
};

async function clearMirroredSessionCookies() {
  const cookieStore = await cookies();
  cookieStore.delete("schoolar_sessionid");
  cookieStore.delete("schoolar_csrftoken");
}

async function writeJson<T>(
  path: string,
  method: "POST" | "PATCH",
  payload: Record<string, unknown>,
): Promise<MutationResult<T>> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      method,
      cache: "no-store",
      headers: new Headers({
        ...Object.fromEntries((await buildHeaders(method)).entries()),
        "Content-Type": "application/json",
      }),
      body: JSON.stringify(payload),
    });

    const data = await parseJsonSafe<T & { error?: { message?: string; details?: unknown } }>(response);
    const errorMessage =
      data && typeof data === "object" && "error" in data && data.error?.message
        ? data.error.message
        : undefined;

    return {
      ok: response.ok,
      statusCode: response.status,
      data,
      error: errorMessage,
    };
  } catch {
    return {
      ok: false,
      statusCode: 0,
      error: "Não foi possível ligar ao backend.",
    };
  }
}

async function deleteJson<T>(path: string): Promise<MutationResult<T>> {
  const baseUrl = resolveApiBaseUrl();

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      method: "DELETE",
      cache: "no-store",
      headers: await buildHeaders("PATCH"),
    });

    const data = await parseJsonSafe<T & { error?: { message?: string } }>(response);
    const errorMessage =
      data && typeof data === "object" && "error" in data && data.error?.message
        ? data.error.message
        : undefined;

    return {
      ok: response.ok,
      statusCode: response.status,
      data,
      error: errorMessage,
    };
  } catch {
    return {
      ok: false,
      statusCode: 0,
      error: "Não foi possível ligar ao backend.",
    };
  }
}

export async function mutateRecord(
  path: string,
  method: "POST" | "PATCH" | "DELETE",
  payload?: Record<string, unknown>,
) {
  if (method === "DELETE") {
    return deleteJson<unknown>(path);
  }
  return writeJson<unknown>(path, method, payload ?? {});
}

async function readJsonWithRetry<T>(
  path: string,
  attempts = 2,
): Promise<{ ok: boolean; statusCode: number; data?: T }> {
  let lastResponse = { ok: false, statusCode: 0 } as {
    ok: boolean;
    statusCode: number;
    data?: T;
  };

  for (let attempt = 0; attempt < attempts; attempt += 1) {
    lastResponse = await readJson<T>(path);
    if (lastResponse.ok || lastResponse.statusCode === 401 || lastResponse.statusCode === 403) {
      return lastResponse;
    }
  }

  return lastResponse;
}

async function readRecord<T>(path: string): Promise<{ ok: boolean; statusCode: number; data?: T }> {
  return readJsonWithRetry<T>(path);
}

function formatReadinessMessage(payload?: ReadinessPayload) {
  if (!payload?.checks) {
    return "Nenhum detalhe de prontidão foi devolvido.";
  }

  const summary = Object.entries(payload.checks)
    .map(([key, value]) => `${key}: ${value}`)
    .join(" | ");

  return `Verificações reportadas: ${summary}.`;
}

function normalizeCollection<T>(payload?: PaginatedResponse<T> | T[]) {
  if (Array.isArray(payload)) {
    return {
      count: payload.length,
      items: payload,
      next: null,
      previous: null,
    };
  }

  if (payload?.results) {
    return {
      count: payload.count ?? payload.results.length,
      items: payload.results,
      next: payload.next ?? null,
      previous: payload.previous ?? null,
    };
  }

  return {
    count: 0,
    items: [] as T[],
    next: null,
    previous: null,
  };
}

function getCollectionMessage(statusCode: number, count: number) {
  if (statusCode === 401 || statusCode === 403) {
    return "Endpoint protegido. Configure API_USERNAME/API_PASSWORD para acesso autenticado.";
  }

  if (statusCode === 0) {
    return "Sem ligação ao backend.";
  }

  if (count === 0) {
    return "O endpoint está acessível, mas não há registos disponíveis.";
  }

  return `${count} registos carregados a partir do backend.`;
}

async function readCollection<T>(path: string): Promise<CollectionSnapshot<T>> {
  const response = await readJsonWithRetry<PaginatedResponse<T> | T[]>(path);
  const normalized = normalizeCollection(response.data);

  return {
    ok: response.ok,
    status:
      response.statusCode === 401 || response.statusCode === 403
        ? "AUTH"
        : response.ok
          ? "ONLINE"
          : "OFFLINE",
    statusCode: response.statusCode,
    count: normalized.count,
    items: normalized.items,
    next: normalized.next,
    previous: normalized.previous,
    message: getCollectionMessage(response.statusCode, normalized.count),
    requiresAuth: response.statusCode === 401 || response.statusCode === 403,
  };
}

async function getPlatformMeta(): Promise<PlatformMeta> {
  const [healthResponse, readinessResponse] = await Promise.all([
    readJsonWithRetry<HealthPayload>("/health/"),
    readJsonWithRetry<ReadinessPayload>("/ready/"),
  ]);

  const baseUrl = resolveApiBaseUrl();

  return {
    baseUrlLabel: baseUrl,
    authConfigured: (await resolveAuthContext()).authMode !== "none",
    tenantId: resolveTenantId(),
    health: {
      ok: healthResponse.ok,
      status: healthResponse.data?.status?.toUpperCase() || "OFFLINE",
      message: healthResponse.ok
        ? "O endpoint respondeu com sucesso e a aplicação está acessível."
        : `Não foi possível alcançar o backend (${healthResponse.statusCode || "sem ligação"}).`,
    },
    readiness: {
      ok: readinessResponse.ok && readinessResponse.data?.status === "ok",
      status: readinessResponse.data?.status?.toUpperCase() || "OFFLINE",
      message:
        readinessResponse.ok && readinessResponse.data
          ? formatReadinessMessage(readinessResponse.data)
          : `A prontidão está indisponível (${readinessResponse.statusCode || "sem ligação"}).`,
    },
  };
}

export async function getAuthSession(): Promise<{ authenticated: boolean; user: AuthUser | null }> {
  const response = await readJsonWithRetry<AuthPayload>(apiPath("/auth/me/"));
  if (!response.ok || !response.data?.user) {
    return { authenticated: false, user: null };
  }

  return {
    authenticated: true,
    user: response.data.user,
  };
}

export async function requireAuthSession(nextPath: string) {
  const session = await getAuthSession();
  if (!session.authenticated || !session.user) {
    redirect(`/login?error=session_expired&next=${encodeURIComponent(nextPath)}`);
  }
  return session.user;
}

export async function handleMutationRedirect(
  result: MutationResult<unknown>,
  pagePath: string,
  successStatus: string,
  errorStatus: string,
) {
  await handleMutationRedirectTo(result, pagePath, successStatus, errorStatus);
}

function appendStatusQuery(pathOrUrl: string, status: string) {
  const resolvedUrl = new URL(pathOrUrl, "http://codex.local");
  resolvedUrl.searchParams.set("status", status);
  return `${resolvedUrl.pathname}${resolvedUrl.search}`;
}

export async function handleMutationRedirectTo(
  result: MutationResult<unknown>,
  pageHref: string,
  successStatus: string,
  errorStatus: string,
) {
  if (result.statusCode === 401 || result.statusCode === 403) {
    await clearMirroredSessionCookies();
    redirect(`/login?error=session_expired&next=${encodeURIComponent(pageHref)}`);
  }

  redirect(appendStatusQuery(pageHref, result.ok ? successStatus : errorStatus));
}

export async function getHomeSnapshot(): Promise<HomeSnapshot> {
  const meta = await getPlatformMeta();
  const [schools, managementAssignments, subjectPlans, periods, components, periodResults] = await Promise.all([
    readCollection<School>(apiPath("/school/schools/")),
    readCollection<ManagementAssignment>(apiPath("/school/management-assignments/")),
    readCollection<SubjectCurriculumPlan>(apiPath("/curriculum/subject-plans/")),
    readCollection<AssessmentPeriod>(apiPath("/assessment/periods/")),
    readCollection<AssessmentComponent>(apiPath("/assessment/components/")),
    readCollection<SubjectPeriodResult>(apiPath("/assessment/subject-period-results/")),
  ]);

  return {
    ...meta,
    schools,
    managementAssignments,
    subjectPlans,
    periods,
    components,
    periodResults,
  };
}

export async function getManagementSnapshot(): Promise<ManagementSnapshot> {
  const meta = await getPlatformMeta();
  const [academicYears, schools, classrooms, enrollments, managementAssignments] = await Promise.all([
    readCollection<AcademicYear>(apiPath("/school/academic-years/")),
    readCollection<School>(apiPath("/school/schools/")),
    readCollection<Classroom>(apiPath("/school/classrooms/")),
    readCollection<Enrollment>(apiPath("/school/enrollments/")),
    readCollection<ManagementAssignment>(apiPath("/school/management-assignments/")),
  ]);

  return {
    ...meta,
    academicYears,
    schools,
    classrooms,
    enrollments,
    managementAssignments,
  };
}

export async function getCurriculumSnapshot(): Promise<CurriculumSnapshot> {
  const meta = await getPlatformMeta();
  const [academicYears, grades, gradeSubjects, subjectPlans] = await Promise.all([
    readCollection<AcademicYear>(apiPath("/school/academic-years/")),
    readCollection<Grade>(apiPath("/school/grades/")),
    readCollection<GradeSubject>(apiPath("/school/grade-subjects/")),
    readCollection<SubjectCurriculumPlan>(apiPath("/curriculum/subject-plans/")),
  ]);

  return {
    ...meta,
    academicYears,
    grades,
    gradeSubjects,
    subjectPlans,
  };
}

export async function getAssessmentSnapshot(): Promise<AssessmentSnapshot> {
  const meta = await getPlatformMeta();
  const [academicYears, classrooms, periods, components, assessments, periodResults] = await Promise.all([
    readCollection<AcademicYear>(apiPath("/school/academic-years/")),
    readCollection<Classroom>(apiPath("/school/classrooms/")),
    readCollection<AssessmentPeriod>(apiPath("/assessment/periods/")),
    readCollection<AssessmentComponent>(apiPath("/assessment/components/")),
    readCollection<Assessment>(apiPath("/assessment/assessments/")),
    readCollection<SubjectPeriodResult>(apiPath("/assessment/subject-period-results/")),
  ]);

  return {
    ...meta,
    academicYears,
    classrooms,
    periods,
    components,
    assessments,
    periodResults,
  };
}

export async function getStudentPortalSnapshot(): Promise<StudentPortalSnapshot> {
  const meta = await getPlatformMeta();
  const [students, enrollments, attendance, assessments, periodResults, invoices, announcements, courses, lessons, assignments, submissions] = await Promise.all([
    readCollection<Student>(apiPath("/academic/students/")),
    readCollection<Enrollment>(apiPath("/school/enrollments/")),
    readCollection<AttendanceRecord>(apiPath("/school/attendance-records/")),
    readCollection<Assessment>(apiPath("/assessment/assessments/")),
    readCollection<SubjectPeriodResult>(apiPath("/assessment/subject-period-results/")),
    readCollection<Invoice>(apiPath("/school/invoices/")),
    readCollection<Announcement>(apiPath("/school/announcements/")),
    readCollection<Course>(apiPath("/learning/courses/")),
    readCollection<Lesson>(apiPath("/learning/lessons/")),
    readCollection<Assignment>(apiPath("/learning/assignments/")),
    readCollection<Submission>(apiPath("/learning/submissions/")),
  ]);

  return {
    ...meta,
    students,
    enrollments,
    attendance,
    assessments,
    periodResults,
    invoices,
    announcements,
    courses,
    lessons,
    assignments,
    submissions,
  };
}

export async function getTeacherPortalSnapshot(): Promise<TeacherPortalSnapshot> {
  const meta = await getPlatformMeta();
  const [teachers, classrooms, enrollments, teachingAssignments, attendance, assessments, announcements, offerings, lessons, assignments, submissions] = await Promise.all([
    readCollection<Teacher>(apiPath("/school/teachers/")),
    readCollection<Classroom>(apiPath("/school/classrooms/")),
    readCollection<Enrollment>(apiPath("/school/enrollments/")),
    readCollection<TeachingAssignment>(apiPath("/school/teaching-assignments/")),
    readCollection<AttendanceRecord>(apiPath("/school/attendance-records/")),
    readCollection<Assessment>(apiPath("/assessment/assessments/")),
    readCollection<Announcement>(apiPath("/school/announcements/")),
    readCollection<CourseOffering>(apiPath("/learning/offerings/")),
    readCollection<Lesson>(apiPath("/learning/lessons/")),
    readCollection<Assignment>(apiPath("/learning/assignments/")),
    readCollection<Submission>(apiPath("/learning/submissions/")),
  ]);

  return {
    ...meta,
    teachers,
    classrooms,
    enrollments,
    teachingAssignments,
    attendance,
    assessments,
    announcements,
    offerings,
    lessons,
    assignments,
    submissions,
  };
}

export async function getFinanceSnapshot(): Promise<FinanceSnapshot> {
  const meta = await getPlatformMeta();
  const [schools, students, guardians, invoices, payments] = await Promise.all([
    readCollection<School>(apiPath("/school/schools/")),
    readCollection<Student>(apiPath("/academic/students/")),
    readCollection<Guardian>(apiPath("/academic/guardians/")),
    readCollection<Invoice>(apiPath("/school/invoices/")),
    readCollection<Payment>(apiPath("/school/payments/")),
  ]);

  return {
    ...meta,
    schools,
    students,
    guardians,
    invoices,
    payments,
  };
}

export async function getCommunicationSnapshot(): Promise<CommunicationSnapshot> {
  const meta = await getPlatformMeta();
  const [announcements, guardians, studentGuardians, classrooms, teachers] = await Promise.all([
    readCollection<Announcement>(apiPath("/school/announcements/")),
    readCollection<Guardian>(apiPath("/academic/guardians/")),
    readCollection<StudentGuardian>(apiPath("/academic/student-guardians/")),
    readCollection<Classroom>(apiPath("/school/classrooms/")),
    readCollection<Teacher>(apiPath("/school/teachers/")),
  ]);

  return {
    ...meta,
    announcements,
    guardians,
    studentGuardians,
    classrooms,
    teachers,
  };
}

export async function getLearningSnapshot(): Promise<LearningSnapshot> {
  const meta = await getPlatformMeta();
  const [courses, offerings, lessons, materials, assignments, submissions] = await Promise.all([
    readCollection<Course>(apiPath("/learning/courses/")),
    readCollection<CourseOffering>(apiPath("/learning/offerings/")),
    readCollection<Lesson>(apiPath("/learning/lessons/")),
    readCollection<LessonMaterial>(apiPath("/learning/lesson-materials/")),
    readCollection<Assignment>(apiPath("/learning/assignments/")),
    readCollection<Submission>(apiPath("/learning/submissions/")),
  ]);

  return {
    ...meta,
    courses,
    offerings,
    lessons,
    materials,
    assignments,
    submissions,
  };
}

export async function getAuditSnapshot(filters?: {
  page?: number;
  resource?: string;
  action?: string;
  severity?: string;
  acknowledged?: string;
  username?: string;
  tenant_id?: string;
  date_from?: string;
  date_to?: string;
}): Promise<AuditSnapshot> {
  const meta = await getPlatformMeta();
  const query = new URLSearchParams();
  if (filters?.page) query.set("page", String(filters.page));
  if (filters?.resource) query.set("resource", filters.resource);
  if (filters?.action) query.set("action", filters.action);
  if (filters?.severity) query.set("severity", filters.severity);
  if (filters?.acknowledged) query.set("acknowledged", filters.acknowledged);
  if (filters?.username) query.set("username", filters.username);
  if (filters?.tenant_id) query.set("tenant_id", filters.tenant_id);
  if (filters?.date_from) query.set("date_from", filters.date_from);
  if (filters?.date_to) query.set("date_to", filters.date_to);
  const auditEvents = await readCollection<AuditEvent>(
    apiPath(`/school/audit-events/${query.toString() ? `?${query}` : ""}`),
  );
  const auditAlerts = await readCollection<AuditAlert>(
    apiPath(`/school/audit-alerts/${query.toString() ? `?${query}` : ""}`),
  );

  return {
    ...meta,
    auditEvents,
    auditAlerts,
  };
}

export async function getReportsSnapshot(): Promise<ReportsSnapshot> {
  const meta = await getPlatformMeta();
  const [reports, catalogResponse, students, academicYears, grades, classrooms, teachers, managementAssignments] = await Promise.all([
    readCollection<ReportRecord>(apiPath("/reports/reports/")),
    readJsonWithRetry<{ results: ReportCatalogItem[] }>(apiPath("/reports/reports/catalog/")),
    readCollection<Student>(apiPath("/academic/students/")),
    readCollection<AcademicYear>(apiPath("/school/academic-years/")),
    readCollection<Grade>(apiPath("/school/grades/")),
    readCollection<Classroom>(apiPath("/school/classrooms/")),
    readCollection<Teacher>(apiPath("/school/teachers/")),
    readCollection<ManagementAssignment>(apiPath("/school/management-assignments/")),
  ]);

  const catalogItems = catalogResponse.data?.results || [];

  return {
    ...meta,
    reports,
    catalog: {
      ok: catalogResponse.ok,
      status:
        catalogResponse.statusCode === 401 || catalogResponse.statusCode === 403
          ? "AUTH"
          : catalogResponse.ok
            ? "ONLINE"
            : "OFFLINE",
      statusCode: catalogResponse.statusCode,
      count: catalogItems.length,
      items: catalogItems,
      next: null,
      previous: null,
      message: getCollectionMessage(catalogResponse.statusCode, catalogItems.length),
      requiresAuth: catalogResponse.statusCode === 401 || catalogResponse.statusCode === 403,
    },
    students,
    academicYears,
    grades,
    classrooms,
    teachers,
    managementAssignments,
  };
}

export async function getReportDetail(id: number) {
  return readRecord<ReportRecord>(apiPath(`/reports/reports/${id}/`));
}

export async function getReportVerification(code: string, hash?: string) {
  const query = new URLSearchParams();
  query.set("code", code);
  if (hash) {
    query.set("hash", hash);
  }
  return readRecord<ReportVerification>(apiPath(`/reports/reports/verify/?${query.toString()}`));
}

export async function createAnnouncement(payload: {
  school: number;
  classroom?: number | null;
  title: string;
  message: string;
  audience: string;
  author?: number | null;
}) {
  return writeJson<Announcement>(apiPath("/school/announcements/"), "POST", payload);
}

export async function updateAnnouncement(id: number, payload: Partial<Announcement>) {
  return writeJson<Announcement>(apiPath(`/school/announcements/${id}/`), "PATCH", payload);
}

export async function createAttendanceRecord(payload: {
  enrollment: number;
  lesson_date: string;
  status: string;
  notes?: string;
}) {
  return writeJson<AttendanceRecord>(apiPath("/school/attendance-records/"), "POST", payload);
}

export async function createLesson(payload: {
  offering: number;
  title: string;
  description?: string;
  scheduled_at: string;
  duration_minutes: number;
  meeting_url?: string;
  recording_url?: string;
  published?: boolean;
}) {
  return writeJson<Lesson>(apiPath("/learning/lessons/"), "POST", payload);
}

export async function updateLesson(id: number, payload: Partial<Lesson>) {
  return writeJson<Lesson>(apiPath(`/learning/lessons/${id}/`), "PATCH", payload);
}

export async function createAssignment(payload: {
  offering: number;
  title: string;
  instructions?: string;
  opens_at: string;
  due_at: string;
  max_score: number;
  published?: boolean;
}) {
  return writeJson<Assignment>(apiPath("/learning/assignments/"), "POST", payload);
}

export async function updateAssignment(id: number, payload: Partial<Assignment>) {
  return writeJson<Assignment>(apiPath(`/learning/assignments/${id}/`), "PATCH", payload);
}

export async function createLessonMaterial(payload: {
  lesson: number;
  title: string;
  material_type: string;
  url: string;
  required?: boolean;
}) {
  return writeJson<LessonMaterial>(apiPath("/learning/lesson-materials/"), "POST", payload);
}

export async function createInvoice(payload: {
  student: number;
  school: number;
  reference: string;
  description: string;
  amount: number;
  due_date: string;
  status?: string;
}) {
  return writeJson<Invoice>(apiPath("/school/invoices/"), "POST", payload);
}

export async function updateInvoice(id: number, payload: Partial<Invoice>) {
  return writeJson<Invoice>(apiPath(`/school/invoices/${id}/`), "PATCH", payload);
}

export async function createPayment(payload: {
  invoice: number;
  amount: number;
  payment_date: string;
  method: string;
  reference?: string;
  notes?: string;
}) {
  return writeJson<Payment>(apiPath("/school/payments/"), "POST", payload);
}

export async function createSubmission(payload: {
  assignment: number;
  student: number;
  submitted_at?: string | null;
  text_response?: string;
  attachment_url?: string;
  status?: string;
}) {
  return writeJson<Submission>(apiPath("/learning/submissions/"), "POST", payload);
}

export async function acknowledgeAuditAlert(id: number) {
  return writeJson<AuditAlert>(apiPath(`/school/audit-alerts/${id}/acknowledge/`), "POST", {});
}

export async function generateReport(payload: {
  report_kind: string;
  student?: number;
  academic_year?: number;
  grade?: number;
  classroom?: number;
  period_scope?: string;
  period_order?: number;
  persist?: boolean;
  title?: string;
}) {
  return writeJson<ReportRecord | GeneratedReportPayload>(apiPath("/reports/reports/generate/"), "POST", payload);
}
