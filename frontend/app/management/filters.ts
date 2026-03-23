import type {
  Classroom,
  Enrollment,
  ManagementAssignment,
  ManagementSnapshot,
} from "@/lib/api";

export type ManagementFilters = {
  school: string;
  year: string;
  role: string;
};

export function formatRole(role: string) {
  return role.replaceAll("_", " ");
}

export function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export function filterClassrooms(snapshot: ManagementSnapshot, filters: ManagementFilters) {
  return snapshot.classrooms.items.filter((item) => {
    if (filters.school && String(item.school) !== filters.school) {
      return false;
    }

    if (filters.year && item.academic_year !== filters.year) {
      return false;
    }

    return true;
  });
}

export function filterEnrollments(snapshot: ManagementSnapshot, filters: ManagementFilters) {
  return snapshot.enrollments.items.filter((item) => {
    if (
      filters.school &&
      !snapshot.classrooms.items.find(
        (classroom) => classroom.id === item.classroom && String(classroom.school) === filters.school,
      )
    ) {
      return false;
    }

    if (filters.year && item.academic_year_code !== filters.year) {
      return false;
    }

    return true;
  });
}

export function filterManagementAssignments(snapshot: ManagementSnapshot, filters: ManagementFilters) {
  return snapshot.managementAssignments.items.filter((item) => {
    if (filters.school && String(item.school) !== filters.school) {
      return false;
    }

    if (filters.year && item.academic_year_code !== filters.year) {
      return false;
    }

    if (filters.role && item.role !== filters.role) {
      return false;
    }

    return true;
  });
}

export function countClassroomsBySchool(classrooms: Classroom[], schoolId: number) {
  return classrooms.filter((classroom) => classroom.school === schoolId).length;
}

export function countEnrollmentsByClassroom(enrollments: Enrollment[], classroomId: number) {
  return enrollments.filter((enrollment) => enrollment.classroom === classroomId).length;
}

export function describeAssignmentScope(assignment: ManagementAssignment) {
  return (
    assignment.classroom_name ||
    (assignment.grade_number ? `Grade ${assignment.grade_number}` : null) ||
    (assignment.cycle ? `Cycle ${assignment.cycle}` : "School-wide scope")
  );
}
