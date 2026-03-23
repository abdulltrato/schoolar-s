const attendanceStatusLabels: Record<string, string> = {
  present: "Presente",
  late: "Atrasado",
  absent: "Falta",
  justified_absence: "Justificada",
};

const submissionStatusLabels: Record<string, string> = {
  submitted: "Submetido",
  pending: "Pendente",
  graded: "Corrigido",
  returned: "Devolvido",
  missing: "Em falta",
};

const announcementAudienceLabels: Record<string, string> = {
  school: "Escola",
  classroom: "Turma",
  teachers: "Professores",
  guardians: "Encarregados",
  students: "Alunos",
};

const invoiceStatusLabels: Record<string, string> = {
  draft: "Rascunho",
  issued: "Emitida",
  paid: "Paga",
  overdue: "Em atraso",
  cancelled: "Cancelada",
};

const paymentMethodLabels: Record<string, string> = {
  cash: "Numerário",
  bank_transfer: "Transferência bancária",
  mobile_money: "Carteira móvel",
  card: "Cartão",
};

const studentStatusLabels: Record<string, string> = {
  active: "Ativo",
  inactive: "Inativo",
  transferred: "Transferido",
  graduated: "Graduado",
  suspended: "Suspenso",
};

const courseModalityLabels: Record<string, string> = {
  online: "Online",
  hybrid: "Híbrido",
  in_person: "Presencial",
  presencial: "Presencial",
};

const auditSeverityLabels: Record<string, string> = {
  watch: "Observação",
  elevated: "Elevado",
};

const auditActionLabels: Record<string, string> = {
  create: "Criação",
  update: "Atualização",
  delete: "Eliminação",
  acknowledge: "Reconhecimento",
};

const materialTypeLabels: Record<string, string> = {
  link: "Link",
  document: "Documento",
  video: "Vídeo",
  audio: "Áudio",
  other: "Outro",
};

const assessmentTypeLabels: Record<string, string> = {
  diagnostic: "Diagnóstica",
  formative: "Formativa",
  summative: "Sumativa",
  test: "Teste",
  exam: "Exame",
  assignment: "Trabalho",
  acs: "ACS",
  acp: "ACP",
};

export function formatAttendanceStatus(status: string) {
  return attendanceStatusLabels[status] || status;
}

export function formatSubmissionStatus(status: string) {
  return submissionStatusLabels[status] || status;
}

export function formatAnnouncementAudience(audience: string) {
  return announcementAudienceLabels[audience] || audience;
}

export function formatInvoiceStatus(status: string) {
  return invoiceStatusLabels[status] || status;
}

export function formatPaymentMethod(method: string) {
  return paymentMethodLabels[method] || method;
}

export function formatStudentStatus(status: string) {
  return studentStatusLabels[status] || status;
}

export function formatCourseModality(modality: string) {
  return courseModalityLabels[modality] || modality;
}

export function formatAuditSeverity(severity: string) {
  return auditSeverityLabels[severity] || severity;
}

export function formatAuditAction(action: string) {
  return auditActionLabels[action] || action;
}

export function formatMaterialType(type: string) {
  return materialTypeLabels[type] || type;
}

export function formatAssessmentType(type: string) {
  return assessmentTypeLabels[type] || type;
}

export function formatPublishedState(published: boolean) {
  return published ? "Publicado" : "Rascunho";
}
