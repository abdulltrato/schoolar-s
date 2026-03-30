import type {
  Classroom,
  Enrollment,
  ManagementAssignment,
  ManagementSnapshot,
} from "@/lib/api";

// Filtros escolhidos pelo usuário na página de gestão.
export type ManagementFilters = {
  school: string;
  year: string;
  role: string;
};

// Converte o role técnico para texto legível.
export function formatRole(role: string) {
  return role.replaceAll("_", " ");
}

// Normaliza leitura de query param (pega primeiro valor).
export function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

// Filtra turmas por escola e ano letivo.
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

// Filtra matrículas garantindo escola (via turma) e ano.
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

// Filtra cargos de gestão por escola, ano e role.
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

// Conta turmas de uma escola.
export function countClassroomsBySchool(classrooms: Classroom[], schoolId: number) {
  return classrooms.filter((classroom) => classroom.school === schoolId).length;
}

// Conta matrículas de uma turma.
export function countEnrollmentsByClassroom(enrollments: Enrollment[], classroomId: number) {
  return enrollments.filter((enrollment) => enrollment.classroom === classroomId).length;
}

// Descreve o escopo do cargo (turma > classe > ciclo > escola).
export function describeAssignmentScope(assignment: ManagementAssignment) {
  return (
    assignment.classroom_name ||
    (assignment.grade_number ? `Classe ${assignment.grade_number}` : null) ||
    (assignment.cycle ? `Ciclo ${assignment.cycle}` : "Âmbito escolar")
  );
}
