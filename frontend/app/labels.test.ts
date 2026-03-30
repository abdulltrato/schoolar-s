import assert from "node:assert/strict";
import test from "node:test";

import {
  formatAnnouncementAudience,
  formatAssessmentType,
  formatAttendanceStatus,
  formatAuditAction,
  formatAuditSeverity,
  formatCourseModality,
  formatInvoiceStatus,
  formatMaterialType,
  formatPaymentMethod,
  formatPublishedState,
  formatStudentStatus,
  formatSubmissionStatus,
} from "../lib/labels.ts";

test("formatters translate known backend values", () => {
  assert.equal(formatAttendanceStatus("present"), "Presente");
  assert.equal(formatSubmissionStatus("graded"), "Corrigido");
  assert.equal(formatAnnouncementAudience("guardians"), "Encarregados");
  assert.equal(formatInvoiceStatus("issued"), "Emitida");
  assert.equal(formatPaymentMethod("bank_transfer"), "Transferência bancária");
  assert.equal(formatStudentStatus("active"), "Ativo");
  assert.equal(formatCourseModality("hybrid"), "Híbrido");
  assert.equal(formatAuditSeverity("watch"), "Observação");
  assert.equal(formatAuditAction("update"), "Atualização");
  assert.equal(formatMaterialType("document"), "Documento");
  assert.equal(formatAssessmentType("formative"), "Formativa");
  assert.equal(formatPublishedState(true), "Publicado");
  assert.equal(formatPublishedState(false), "Rascunho");
});

test("formatters preserve unknown values", () => {
  assert.equal(formatAttendanceStatus("custom_status"), "custom_status");
  assert.equal(formatSubmissionStatus("custom_submission"), "custom_submission");
  assert.equal(formatAnnouncementAudience("custom_audience"), "custom_audience");
  assert.equal(formatInvoiceStatus("custom_invoice"), "custom_invoice");
  assert.equal(formatPaymentMethod("custom_payment"), "custom_payment");
  assert.equal(formatStudentStatus("custom_student"), "custom_student");
  assert.equal(formatCourseModality("custom_modality"), "custom_modality");
  assert.equal(formatAuditSeverity("custom_severity"), "custom_severity");
  assert.equal(formatAuditAction("custom_action"), "custom_action");
  assert.equal(formatMaterialType("custom_material"), "custom_material");
  assert.equal(formatAssessmentType("custom_assessment"), "custom_assessment");
});
