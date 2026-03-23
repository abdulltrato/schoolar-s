import Link from "next/link";
import { notFound } from "next/navigation";
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
      <section className="rounded-[1rem] border border-ink/10 bg-white/95 p-4 shadow-card document-sheet">
        <div className="print-hidden flex flex-wrap items-center justify-between gap-3 border-b border-ink/10 pb-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Pré-visualização documental</p>
            <p className="mt-1 text-sm text-ink/70">Gerado em {formatDateTime(report.generated_at)}</p>
          </div>
          <PrintReportButton />
        </div>

        <header className="mt-4 border-b border-ink/10 pb-4">
          <p className="text-center text-[11px] font-semibold uppercase tracking-[0.24em] text-ink/55">Substrato Educação</p>
          <h2 className="mt-2 text-center font-display text-2xl font-bold text-ink">{report.title}</h2>
          <p className="mt-2 text-center text-sm leading-6 text-ink/70">
            {renderScalar(metadata.school)} | {renderScalar(metadata.academic_year)} | {renderScalar(metadata.period_label || report.period)}
          </p>
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
            title="Linhas do relatório"
            description="Estrutura tabular ou listagem produzida para pautas, listas e relatórios operacionais."
          />
          <div className="mt-3">{renderRows(rows)}</div>
        </section>
      </section>
    </DashboardShell>
  );
}
