import assert from "node:assert/strict";
import test from "node:test";

import type { ManagementSnapshot } from "../../lib/api";

import {
  countClassroomsBySchool,
  countEnrollmentsByClassroom,
  describeAssignmentScope,
  filterClassrooms,
  filterEnrollments,
  filterManagementAssignments,
  formatRole,
  readParam,
} from "./filters.ts";

function createCollection<T>(items: T[]) {
  return {
    ok: true,
    status: "ONLINE",
    statusCode: 200,
    count: items.length,
    items,
    next: null,
    previous: null,
    message: `${items.length} registos carregados a partir do backend.`,
    requiresAuth: false,
  };
}

function createSnapshot(): ManagementSnapshot {
  return {
    baseUrlLabel: "http://localhost:8000",
    authConfigured: false,
    tenantId: null,
    health: {
      ok: true,
      status: "ONLINE",
      message: "ok",
    },
    readiness: {
      ok: true,
      status: "OK",
      message: "ok",
    },
    academicYears: createCollection([
      {
        id: 1,
        code: "2025",
        start_date: "2025-01-01",
        end_date: "2025-12-31",
        active: true,
      },
      {
        id: 2,
        code: "2026",
        start_date: "2026-01-01",
        end_date: "2026-12-31",
        active: true,
      },
    ]),
    schools: createCollection([
      {
        id: 1,
        code: "ESC-01",
        name: "Escola Central",
        district: "A",
        province: "Maputo",
        active: true,
      },
      {
        id: 2,
        code: "ESC-02",
        name: "Escola Norte",
        district: "B",
        province: "Gaza",
        active: true,
      },
    ]),
    classrooms: createCollection([
      {
        id: 10,
        name: "7A",
        tenant_id: "school-central",
        school: 1,
        school_name: "Escola Central",
        grade: 7,
        grade_name: "Classe 7",
        cycle: 2,
        academic_year: "2025",
        lead_teacher: 90,
        lead_teacher_name: "Ana",
      },
      {
        id: 11,
        name: "8B",
        tenant_id: "school-north",
        school: 2,
        school_name: "Escola Norte",
        grade: 8,
        grade_name: "Classe 8",
        cycle: 2,
        academic_year: "2026",
        lead_teacher: 91,
        lead_teacher_name: "Beto",
      },
    ]),
    enrollments: createCollection([
      {
        id: 100,
        student: 1,
        student_name: "Carla",
        classroom: 10,
        classroom_name: "7A",
        enrollment_date: "2025-01-03",
        school_name: "Escola Central",
        academic_year_code: "2025",
        grade_number: 7,
      },
      {
        id: 101,
        student: 2,
        student_name: "Dino",
        classroom: 11,
        classroom_name: "8B",
        enrollment_date: "2026-01-03",
        school_name: "Escola Norte",
        academic_year_code: "2026",
        grade_number: 8,
      },
    ]),
    managementAssignments: createCollection([
      {
        id: 1000,
        teacher: 90,
        teacher_name: "Ana",
        school: 1,
        school_name: "Escola Central",
        academic_year: 1,
        academic_year_code: "2025",
        role: "homeroom_director",
        grade: 7,
        grade_number: 7,
        classroom: 10,
        classroom_name: "7A",
        cycle: 2,
        active: true,
      },
      {
        id: 1001,
        teacher: 91,
        teacher_name: "Beto",
        school: 2,
        school_name: "Escola Norte",
        academic_year: 2,
        academic_year_code: "2026",
        role: "cycle_director",
        grade: null,
        grade_number: undefined,
        classroom: null,
        classroom_name: undefined,
        cycle: 2,
        active: true,
      },
    ]),
  };
}

test("readParam normalizes strings and arrays", () => {
  assert.equal(readParam("abc"), "abc");
  assert.equal(readParam(["abc", "def"]), "abc");
  assert.equal(readParam(undefined), "");
});

test("formatRole replaces underscores with spaces", () => {
  assert.equal(formatRole("homeroom_director"), "homeroom director");
});

test("filterClassrooms applies school and year filters", () => {
  const snapshot = createSnapshot();
  const result = filterClassrooms(snapshot, {
    school: "1",
    year: "2025",
    role: "",
  });

  assert.deepEqual(result.map((item) => item.id), [10]);
});

test("filterEnrollments uses the classroom to filter by school", () => {
  const snapshot = createSnapshot();
  const result = filterEnrollments(snapshot, {
    school: "2",
    year: "",
    role: "",
  });

  assert.deepEqual(result.map((item) => item.id), [101]);
});

test("filterManagementAssignments combines school, year, and role", () => {
  const snapshot = createSnapshot();
  const result = filterManagementAssignments(snapshot, {
    school: "2",
    year: "2026",
    role: "cycle_director",
  });

  assert.deepEqual(result.map((item) => item.id), [1001]);
});

test("helpers count classrooms and enrollments correctly", () => {
  const snapshot = createSnapshot();

  assert.equal(countClassroomsBySchool(snapshot.classrooms.items, 1), 1);
  assert.equal(countEnrollmentsByClassroom(snapshot.enrollments.items, 10), 1);
});

test("describeAssignmentScope prioritizes classroom, then grade, then cycle", () => {
  const snapshot = createSnapshot();

  assert.equal(describeAssignmentScope(snapshot.managementAssignments.items[0]), "7A");
  assert.equal(describeAssignmentScope(snapshot.managementAssignments.items[1]), "Ciclo 2");
});
