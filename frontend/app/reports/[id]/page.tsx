import Link from "next/link";
import { notFound } from "next/navigation";
import { DocumentSeal } from "@/components/document-seal";
import { DashboardShell } from "@/components/dashboard-shell";
import { PrintReportButton } from "@/components/print-report-button";
import { SectionTitle } from "@/components/section-title";
import { getReportDetail, requireAuthSession } from "@/lib/api";

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "full",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatLabel(value: string) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function renderScalar(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "Sem valor";
  }
  if (typeof value === "boolean") {
    return value ? "Sim" : "Não";
  }
  return String(value);
}

function renderObjectEntries(data: Record<string, unknown>) {
  return (
    <dl className="grid gap-2 sm:grid-cols-2">
      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="rounded-[0.85rem] border border-ink/10 bg-white px-3 py-2">
          <dt className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink/55">{formatLabel(key)}</dt>
          <dd className="mt-1 text-sm leading-5 text-ink/75">{renderScalar(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

function formatDocumentKind(value?: string) {
  switch (value) {
    case "student_declaration":
      return "Declaração";
    case "student_certificate":
      return "Certificado";
    case "student_diploma":
      return "Diploma";
    case "student_progress_report":
      return "Relatório de aproveitamento";
    case "quarterly_grade_sheet":
      return "Pauta trimestral";
    case "semester_grade_sheet":
      return "Pauta semestral";
    case "annual_grade_sheet":
      return "Pauta anual";
    default:
      return formatLabel(value || "documento");
  }
}

function renderDocumentBody(reportKind: string | undefined, studentSnapshot: Record<string, unknown>, metadata: Record<string, unknown>, summary: Record<string, unknown>) {
  const studentName = renderScalar(studentSnapshot.name);
  const grade = renderScalar(studentSnapshot.grade || metadata.grade);
  const classroom = renderScalar(studentSnapshot.classroom || metadata.classroom);
  const year = renderScalar(studentSnapshot.academic_year || metadata.academic_year);
  const school = renderScalar(studentSnapshot.school || metadata.school);
  const statement = renderScalar(summary.statement);
  const average = renderScalar((summary.performance as { overall_average?: unknown } | undefined)?.overall_average);

  if (reportKind === "student_declaration") {
    return (
      <div className="space-y-4 text-[15px] leading-8 text-ink/85">
        <p>
          Para os devidos efeitos, declara-se que <strong>{studentName}</strong> se encontra inscrito e registado nesta instituição de ensino,
          frequentando a <strong>{grade}.ª classe</strong>, turma <strong>{classroom}</strong>, no ano letivo <strong>{year}</strong>, na escola <strong>{school}</strong>.
        </p>
        <p>{statement} Este documento contém selo criptográfico de emissão e pode ser validado pelo código constante no rodapé.</p>
      </div>
    );
  }

  if (reportKind === "student_certificate") {
    return (
      <div className="space-y-4 text-[15px] leading-8 text-ink/85">
        <p>
          Certifica-se que <strong>{studentName}</strong> frequentou regularmente a <strong>{grade}.ª classe</strong>, turma <strong>{classroom}</strong>,
          referente ao ano letivo <strong>{year}</strong>, na escola <strong>{school}</strong>.
        </p>
        <p>
          O presente certificado resume o percurso académico observado no período indicado e regista, quando aplicável, uma média global de <strong>{average}</strong> valores.
        </p>
      </div>
    );
  }

  if (reportKind === "student_diploma") {
    return (
      <div className="space-y-4 text-[15px] leading-8 text-ink/85">
        <p>
          A direção da escola <strong>{school}</strong> reconhece, por este diploma, o percurso académico de <strong>{studentName}</strong>,
          associado à <strong>{grade}.ª classe</strong> no ano letivo <strong>{year}</strong>.
        </p>
        <p>
          Este documento é emitido em formato verificável e apenas deve ser considerado autêntico quando o código de verificação e a assinatura coincidirem com o registo oficial.
        </p>
      </div>
    );
  }

  if (reportKind === "student_progress_report") {
    return (
      <div className="space-y-4 text-[15px] leading-8 text-ink/85">
        <p>
          Relatório individual de aproveitamento de <strong>{studentName}</strong>, referente à <strong>{grade}.ª classe</strong>, turma <strong>{classroom}</strong>,
          no ano letivo <strong>{year}</strong>.
        </p>
        <p>
          A média global registada no sistema é de <strong>{average}</strong> valores, com base nas avaliações e consolidações oficiais disponíveis no backend.
        </p>
      </div>
    );
  }

  return null;
}

function renderRows(rows: Array<Record<string, unknown>>) {
  if (rows.length === 0) {
    return (
      <div className="rounded-[0.9rem] border border-dashed border-ink/15 px-3 py-4 text-sm text-ink/55">
        Sem linhas detalhadas para este relatório.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {rows.map((row, index) => (
        <article key={`row-${index + 1}`} className="rounded-[0.9rem] border border-ink/10 bg-white px-3 py-3">
          <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink/50">Linha {index + 1}</p>
          <div className="mt-2">{renderObjectEntries(row)}</div>
        </article>
      ))}
    </div>
  );
}

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function ReportDetailPage({ params }: PageProps) {
  await requireAuthSession("/reports");
  const resolved = await params;
  const reportId = Number(resolved.id);

  if (!Number.isFinite(reportId) || reportId <= 0) {
    notFound();
  }

  const response = await getReportDetail(reportId);
  if (!response.ok || !response.data) {
    notFound();
  }

  const report = response.data;
  const content = (report.content || {}) as {
    metadata?: Record<string, unknown>;
    student_snapshot?: Record<string, unknown>;
    summary?: Record<string, unknown>;
    rows?: Array<Record<string, unknown>>;
    report_kind?: string;
  };

  const summary = content.summary || {};
  const metadata = content.metadata || {};
  const studentSnapshot = content.student_snapshot || {};
  const rows = Array.isArray(content.rows) ? content.rows : [];
  const reportKind = content.report_kind;
  const formalDocument = Boolean(
    reportKind && ["student_declaration", "student_certificate", "student_diploma", "student_progress_report"].includes(reportKind),
  );
  const documentBody = renderDocumentBody(reportKind, studentSnapshot, metadata, summary);

  return (
    <DashboardShell
      title={report.title}
      description="Leitura detalhada do documento gerado, pronta para impressão ou conferência operacional."
      aside={(
        <div className="print-hidden space-y-3">
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Documento"
              title="Ações rápidas"
              description="Use a vista detalhada para conferência, impressão e futura exportação."
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <PrintReportButton />
              <a
                href={`/api/v1/reports/reports/${report.id}/export/?export_format=html`}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-ink/10 bg-white px-3 py-1.5 text-xs font-semibold text-ink transition hover:border-ink/30"
              >
                Abrir HTML formal
              </a>
              <a
                href={`/api/v1/reports/reports/${report.id}/export/?export_format=pdf`}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-ink/10 bg-white px-3 py-1.5 text-xs font-semibold text-ink transition hover:border-ink/30"
              >
                Exportar PDF
              </a>
              <Link
                href="/reports"
                className="rounded-full border border-ink/10 bg-white px-3 py-1.5 text-xs font-semibold text-ink transition hover:border-ink/30"
              >
                Voltar aos relatórios
              </Link>
            </div>
          </section>
          <section className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Identificação</p>
            <dl className="mt-3 space-y-2 text-sm text-ink/75">
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-ink/55">Tipo</dt>
                <dd>{report.type}</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-ink/55">Chave</dt>
                <dd>{content.report_kind || "Sem chave"}</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-ink/55">Gerado em</dt>
                <dd>{formatDateTime(report.generated_at)}</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-ink/55">Código</dt>
                <dd>{report.verification_code}</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.12em] text-ink/55">Assinatura</dt>
                <dd className="break-all text-xs">{report.verification_hash}</dd>
              </div>
            </dl>
          </section>
        </div>
      )}
    >
      <section className="relative overflow-hidden rounded-[1rem] border border-ink/10 bg-white/95 p-4 shadow-card document-sheet">
        {formalDocument ? (
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 flex items-center justify-center opacity-[0.045] print:opacity-[0.07]">
            <p className="rotate-[-28deg] text-6xl font-bold uppercase tracking-[0.4em] text-ink">Autenticado</p>
          </div>
        ) : null}
        <div className="print-hidden flex flex-wrap items-center justify-between gap-3 border-b border-ink/10 pb-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Pré-visualização documental</p>
            <p className="mt-1 text-sm text-ink/70">Gerado em {formatDateTime(report.generated_at)}</p>
          </div>
          <PrintReportButton />
        </div>

        <header className="mt-4 border-b border-ink/10 pb-4">
          <div className={`grid gap-4 ${formalDocument ? "lg:grid-cols-[1fr_auto]" : ""}`}>
            <div>
              <p className="text-center text-[11px] font-semibold uppercase tracking-[0.24em] text-ink/55">Substrato Educação</p>
              <h2 className="mt-2 text-center font-display text-2xl font-bold text-ink">{report.title}</h2>
              <p className="mt-2 text-center text-sm leading-6 text-ink/70">
                {renderScalar(metadata.school)} | {renderScalar(metadata.academic_year)} | {renderScalar(metadata.period_label || report.period)}
              </p>
              <p className="mt-3 text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-ink/50">
                {formatDocumentKind(reportKind)}
              </p>
            </div>
            {formalDocument ? (
              <div className="mx-auto lg:mx-0">
                <DocumentSeal code={report.verification_code} hash={report.verification_hash} />
              </div>
            ) : null}
          </div>
          <div className="mt-4 rounded-[0.9rem] border border-fern/20 bg-fern/10 px-4 py-3 text-center text-sm text-fern">
            Documento assinado pelo sistema.
            {" "}
            Código: <span className="font-semibold">{report.verification_code}</span>
            {" "}
            |
            {" "}
            <Link href={`/verify-report?code=${encodeURIComponent(report.verification_code)}&hash=${encodeURIComponent(report.verification_hash)}`} className="font-semibold underline underline-offset-2">
              Validar autenticidade
            </Link>
          </div>
        </header>

        {formalDocument && documentBody ? (
          <section className="mt-5 rounded-[1rem] border border-ink/10 bg-sand/35 px-5 py-6">
            <SectionTitle
              eyebrow="Corpo documental"
              title="Texto oficial emitido"
              description="Versão formal para impressão, com identificação, contexto e selo verificável."
            />
            <div className="mt-4">{documentBody}</div>
            <div className="mt-8 grid gap-6 border-t border-ink/10 pt-6 md:grid-cols-2">
              <div>
                <p className="text-sm text-ink/65">Emitido eletronicamente em {formatDateTime(report.generated_at)}</p>
                <p className="mt-10 border-t border-ink/20 pt-2 text-sm font-semibold text-ink/75">Direção da escola</p>
              </div>
              <div>
                <p className="text-sm text-ink/65">Validação externa disponível pelo código {report.verification_code}</p>
                <p className="mt-10 border-t border-ink/20 pt-2 text-sm font-semibold text-ink/75">Secretaria académica</p>
              </div>
            </div>
          </section>
        ) : null}

        {Object.keys(studentSnapshot).length > 0 ? (
          <section className="mt-5">
            <SectionTitle
              eyebrow="Estudante"
              title="Identificação do beneficiário"
              description="Dados base usados para a composição do documento."
            />
            <div className="mt-3">{renderObjectEntries(studentSnapshot)}</div>
          </section>
        ) : null}

        {Object.keys(metadata).length > 0 ? (
          <section className="mt-5">
            <SectionTitle
              eyebrow="Contexto"
              title="Metadados do relatório"
              description="Recorte académico e organizacional aplicado na geração."
            />
            <div className="mt-3">{renderObjectEntries(metadata)}</div>
          </section>
        ) : null}

        {Object.keys(summary).length > 0 ? (
          <section className="mt-5">
            <SectionTitle
              eyebrow="Síntese"
              title="Resumo produzido"
              description="Saída principal da geração, incluindo estatísticas, declaração textual ou indicadores agregados."
            />
            <div className="mt-3">
              {renderObjectEntries(
                Object.fromEntries(
                  Object.entries(summary).filter(([, value]) => !Array.isArray(value) && typeof value !== "object"),
                ),
              )}
            </div>
            {Object.entries(summary)
              .filter(([, value]) => Array.isArray(value) || (value && typeof value === "object"))
              .map(([key, value]) => (
                <div key={key} className="mt-3 rounded-[0.9rem] border border-ink/10 bg-sand/70 p-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink/55">{formatLabel(key)}</p>
                  <div className="mt-2">
                    {Array.isArray(value)
                      ? renderRows(value as Array<Record<string, unknown>>)
                      : renderObjectEntries(value as Record<string, unknown>)}
                  </div>
                </div>
              ))}
          </section>
        ) : null}

        <section className="mt-5">
          <SectionTitle
            eyebrow="Detalhe"
            title={formalDocument ? "Anexos e estruturas" : "Linhas do relatório"}
            description={formalDocument ? "Anexos operacionais usados para fundamentar o documento emitido." : "Estrutura tabular ou listagem produzida para pautas, listas e relatórios operacionais."}
          />
          <div className="mt-3">{renderRows(rows)}</div>
        </section>

        <footer className="mt-6 border-t border-ink/10 pt-4 text-xs leading-5 text-ink/60">
          Assinatura criptográfica: <span className="break-all">{report.verification_hash}</span>
        </footer>
      </section>
    </DashboardShell>
  );
}
