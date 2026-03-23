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
  competency: number;
  competency_name: string;
  level: string;
  updated_at: string;
};

export type Student = {
  id: number;
  name: string;
  birth_date: string;
  grade: number;
  cycle: number;
  status: string;
  competencies: StudentCompetency[];
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
  number: number;
  cycle: number;
  education_level: string;
  name: string;
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
  school: number | null;
  school_name?: string;
  name: string;
  specialty: string;
};

export type Classroom = {
  id: number;
  name: string;
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

function resolveApiBaseUrl() {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

function resolveTenantId() {
  return process.env.API_TENANT_ID || process.env.NEXT_PUBLIC_TENANT_ID || null;
}

function resolveBasicAuthHeader() {
  const username = process.env.API_USERNAME;
  const password = process.env.API_PASSWORD;

  if (!username || !password) {
    return null;
  }

  return `Basic ${Buffer.from(`${username}:${password}`).toString("base64")}`;
}

function buildHeaders() {
  const headers = new Headers({
    Accept: "application/json",
  });

  const authHeader = resolveBasicAuthHeader();
  const tenantId = resolveTenantId();

  if (authHeader) {
    headers.set("Authorization", authHeader);
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
      headers: buildHeaders(),
    });

    const data = await parseJsonSafe<T>(response);
    return { ok: response.ok, statusCode: response.status, data };
  } catch {
    return { ok: false, statusCode: 0 };
  }
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

function formatReadinessMessage(payload?: ReadinessPayload) {
  if (!payload?.checks) {
    return "No readiness details were returned.";
  }

  const summary = Object.entries(payload.checks)
    .map(([key, value]) => `${key}: ${value}`)
    .join(" | ");

  return `Reported checks: ${summary}.`;
}

function normalizeCollection<T>(payload?: PaginatedResponse<T> | T[]) {
  if (Array.isArray(payload)) {
    return {
      count: payload.length,
      items: payload,
    };
  }

  if (payload?.results) {
    return {
      count: payload.count ?? payload.results.length,
      items: payload.results,
    };
  }

  return {
    count: 0,
    items: [] as T[],
  };
}

function getCollectionMessage(statusCode: number, count: number) {
  if (statusCode === 401 || statusCode === 403) {
    return "Protected endpoint. Configure API_USERNAME/API_PASSWORD for authenticated access.";
  }

  if (statusCode === 0) {
    return "No connection to the backend.";
  }

  if (count === 0) {
    return "Endpoint is reachable, but no records are available.";
  }

  return `${count} records loaded from the backend.`;
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
    authConfigured: Boolean(resolveBasicAuthHeader()),
    tenantId: resolveTenantId(),
    health: {
      ok: healthResponse.ok,
      status: healthResponse.data?.status?.toUpperCase() || "OFFLINE",
      message: healthResponse.ok
        ? "The endpoint responded successfully and the application is reachable."
        : `Could not reach the backend (${healthResponse.statusCode || "no connection"}).`,
    },
    readiness: {
      ok: readinessResponse.ok && readinessResponse.data?.status === "ok",
      status: readinessResponse.data?.status?.toUpperCase() || "OFFLINE",
      message:
        readinessResponse.ok && readinessResponse.data
          ? formatReadinessMessage(readinessResponse.data)
          : `Readiness is unavailable (${readinessResponse.statusCode || "no connection"}).`,
    },
  };
}

export async function getHomeSnapshot(): Promise<HomeSnapshot> {
  const meta = await getPlatformMeta();
  const [schools, managementAssignments, subjectPlans, periods, components, periodResults] = await Promise.all([
    readCollection<School>("/api/v1/school/schools/"),
    readCollection<ManagementAssignment>("/api/v1/school/management-assignments/"),
    readCollection<SubjectCurriculumPlan>("/api/v1/curriculum/subject-plans/"),
    readCollection<AssessmentPeriod>("/api/v1/assessment/periods/"),
    readCollection<AssessmentComponent>("/api/v1/assessment/components/"),
    readCollection<SubjectPeriodResult>("/api/v1/assessment/subject-period-results/"),
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
    readCollection<AcademicYear>("/api/v1/school/academic-years/"),
    readCollection<School>("/api/v1/school/schools/"),
    readCollection<Classroom>("/api/v1/school/classrooms/"),
    readCollection<Enrollment>("/api/v1/school/enrollments/"),
    readCollection<ManagementAssignment>("/api/v1/school/management-assignments/"),
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
    readCollection<AcademicYear>("/api/v1/school/academic-years/"),
    readCollection<Grade>("/api/v1/school/grades/"),
    readCollection<GradeSubject>("/api/v1/school/grade-subjects/"),
    readCollection<SubjectCurriculumPlan>("/api/v1/curriculum/subject-plans/"),
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
    readCollection<AcademicYear>("/api/v1/school/academic-years/"),
    readCollection<Classroom>("/api/v1/school/classrooms/"),
    readCollection<AssessmentPeriod>("/api/v1/assessment/periods/"),
    readCollection<AssessmentComponent>("/api/v1/assessment/components/"),
    readCollection<Assessment>("/api/v1/assessment/assessments/"),
    readCollection<SubjectPeriodResult>("/api/v1/assessment/subject-period-results/"),
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
