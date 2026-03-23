import Link from "next/link";
import { revalidatePath } from "next/cache";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
import {
  generateReport,
  getReportsSnapshot,
  handleMutationRedirect,
  requireAuthSession,
  type ManagementAssignment,
  type ReportCatalogItem,
  type ReportRecord,
  type Student,
} from "@/lib/api";

function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatReportType(value: string) {
  if (value === "student") {
    return "Aluno";
  }
  if (value === "school") {
    return "Escola";
  }
  if (value === "national") {
    return "Nacional";
  }
  return value;
}

function humanizeRequirement(value: string) {
  if (value === "student") {
    return "Estudante";
  }
  if (value === "academic_year") {
    return "Ano letivo";
  }
  if (value === "grade") {
    return "Classe";
  }
  if (value === "classroom") {
    return "Turma";
  }
  return value;
}

async function generateReportAction(formData: FormData) {
  "use server";

  const payload: {
    report_kind: string;
    student?: number;
    academic_year?: number;
    grade?: number;
    classroom?: number;
    period_scope?: string;
    period_order?: number;
    persist: true;
    title?: string;
  } = {
    report_kind: String(formData.get("report_kind") || ""),
    persist: true,
  };

  const student = Number(formData.get("student") || 0);
  const academicYear = Number(formData.get("academic_year") || 0);
  const grade = Number(formData.get("grade") || 0);
  const classroom = Number(formData.get("classroom") || 0);
  const periodScope = String(formData.get("period_scope") || "").trim();
  const periodOrder = Number(formData.get("period_order") || 0);
  const title = String(formData.get("title") || "").trim();

  if (student > 0) payload.student = student;
  if (academicYear > 0) payload.academic_year = academicYear;
  if (grade > 0) payload.grade = grade;
  if (classroom > 0) payload.classroom = classroom;
  if (periodScope) payload.period_scope = periodScope;
  if (periodOrder > 0) payload.period_order = periodOrder;
  if (title) payload.title = title;

  const result = await generateReport(payload);
  revalidatePath("/reports");
  await handleMutationRedirect(result, "/reports", "report-generated", "report-error");
}

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

const panelClass = "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/94 p-4 shadow-[0_20px_65px_rgba(20,33,61,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_25px_70px_rgba(20,33,61,0.18)]";
const statusClasses = {
  success: "border-fern/20 bg-fern/10 text-fern",
  danger: "border-ember/20 bg-ember/10 text-ember",
};
const sideBadge = "rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70";
const inputControl = "w-full rounded-[1rem] border border-ink/10 bg-white px-3 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(0,0,0,0.05)] outline-none transition placeholder:text-ink/40 focus:border-ink/30 focus:ring-4 focus:ring-mist";

export default async function ReportsPage({ searchParams }: PageProps) {
  await requireAuthSession("/reports");
  const snapshot = await getReportsSnapshot();
  const params = (await searchParams) || {};
  const status = readParam(params.status);
  const reportKind = readParam(params.kind);
  const year = readParam(params.year);
  const grade = readParam(params.grade);
  const classroom = readParam(params.classroom);

  const filteredCatalog = snapshot.catalog.items.filter((item) => {
    if (reportKind && item.key !== reportKind) {
      return false;
    }
    return true;
  });

  const filteredReports = snapshot.reports.items.filter((item) => {
    const content = item.content as { report_kind?: string; metadata?: { academic_year?: string; grade?: number; classroom?: string } };
    if (reportKind && content.report_kind !== reportKind) {
      return false;
    }
    if (year && content.metadata?.academic_year !== year) {
      return false;
    }
    if (grade && String(content.metadata?.grade || "") !== grade) {
      return false;
    }
    if (classroom && content.metadata?.classroom !== classroom) {
      return false;
    }
    return true;
  });

  const directorRows = snapshot.managementAssignments.items.filter((item) => item.active).slice(0, 6);

  return (
    <DashboardShell
      title="Relatórios e documentos"
      description="Geração assistida de declarações, certificados, diplomas, pautas, listas operacionais e relatórios estatísticos."
      aside={(
        <>
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Resumo"
              title="Motor documental"
              description="A consola une documentos individuais, listas operacionais e pautas com base no backend."
            />
            <dl className="mt-5 space-y-4 text-sm leading-6">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Modelos</dt>
                <dd className="text-lg font-semibold">{snapshot.catalog.count} disponíveis</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Relatórios</dt>
                <dd className="text-lg font-semibold">{snapshot.reports.count} persistidos</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Base escolar</dt>
                <dd className="text-lg font-semibold">{snapshot.students.count} estudantes · {snapshot.teachers.count} professores · {snapshot.classrooms.count} turmas</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária de relatórios" className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-white/85 p-4 shadow-[0_20px_50px_rgba(20,33,61,0.08)]">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/60">Secções</p>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#generator">
                  Gerador
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#catalog">
                  Catálogo
                </a>
              </li>
              <li>
                <a className="block rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2 transition hover:border-ink/30 hover:bg-ink/10" href="#history">
                  Histórico
                </a>
              </li>
            </ul>
          </nav>
        </>
      )}
    >
      <section className="overflow-hidden rounded-[1.5rem] border border-white/65 bg-[linear-gradient(135deg,rgba(20,33,61,0.95),rgba(32,52,85,0.9))] p-5 text-sand shadow-card shadow-[0_30px_80px_rgba(20,33,61,0.18)]">
        <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Relatórios</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Motor documental orientado por contexto escolar.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Gere declarações, certificados e pautas com filtros inteligentes e base institucional limpa. O histórico mostra o que já foi persistido.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Catálogo</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.catalog.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Relatórios</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.reports.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Registos</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.students.count + snapshot.teachers.count}</p>
            </div>
          </div>
        </div>
      </section>

      {status ? (
        <section
          className={`mt-4 rounded-[1.15rem] border px-4 py-3 text-sm ${status === "report-error" ? statusClasses.danger : statusClasses.success}`}
        >
          {status === "report-generated" && "Relatório gerado e guardado com sucesso."}
          {status === "report-error" && "Não foi possível gerar o relatório pedido."}
        </section>
      ) : null}

      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_50px_rgba(20,33,61,0.06)]">
        <FilterBar
        fields={[
          {
            name: "kind",
            label: "Tipo",
            value: reportKind,
            options: snapshot.catalog.items.map((item) => ({
              value: item.key,
              label: item.label,
            })),
          },
          {
            name: "year",
            label: "Ano letivo",
            value: year,
            options: snapshot.academicYears.items.map((item) => ({
              value: item.code,
              label: item.code,
            })),
          },
          {
            name: "grade",
            label: "Classe",
            value: grade,
            options: snapshot.grades.items.map((item) => ({
              value: String(item.number),
              label: item.name,
            })),
          },
          {
            name: "classroom",
            label: "Turma",
            value: classroom,
            options: snapshot.classrooms.items.map((item) => ({
              value: item.name,
              label: `${item.name} | ${item.grade_name || `Classe ${item.grade}`}`,
            })),
          },
        ]}
        />
      </div>

      <section id="generator" className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className={panelClass}>
          <SectionTitle
            eyebrow="Gerar"
            title="Orquestrador de documentos"
            description="Escolha o tipo de saída e o contexto académico. O backend decide a estrutura e persiste o documento."
          />
          <form action={generateReportAction} className="mt-4 grid gap-3 md:grid-cols-2">
            <select name="report_kind" defaultValue={reportKind} required className={inputControl}>
              <option value="">Selecionar tipo de geração</option>
              {snapshot.catalog.items.map((item) => (
                <option key={item.key} value={item.key}>{item.label}</option>
              ))}
            </select>
            <input name="title" placeholder="Título opcional" className={inputControl} />
            <select name="student" className={inputControl}>
              <option value="">Sem estudante específico</option>
              {snapshot.students.items.map((item) => (
                <option key={item.id} value={item.id}>{item.name} | Classe {item.grade}</option>
              ))}
            </select>
            <select name="academic_year" defaultValue={snapshot.academicYears.items[0]?.id ? String(snapshot.academicYears.items[0].id) : ""} className={inputControl}>
              <option value="">Sem ano letivo</option>
              {snapshot.academicYears.items.map((item) => (
                <option key={item.id} value={item.id}>{item.code}</option>
              ))}
            </select>
            <select name="grade" className={inputControl}>
              <option value="">Sem classe específica</option>
              {snapshot.grades.items.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
            <select name="classroom" className={inputControl}>
              <option value="">Sem turma específica</option>
              {snapshot.classrooms.items.map((item) => (
                <option key={item.id} value={item.id}>{item.name} | {item.academic_year}</option>
              ))}
            </select>
            <select name="period_scope" className={inputControl}>
              <option value="">Escopo automático</option>
              <option value="quarterly">Trimestral</option>
              <option value="semester">Semestral</option>
              <option value="annual">Anual</option>
            </select>
            <select name="period_order" className={inputControl}>
              <option value="">Período automático</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
            <div className="md:col-span-2">
              <SubmitButton idleLabel="Gerar e guardar relatório" pendingLabel="A gerar relatório..." className="w-full px-4 py-3" />
            </div>
          </form>
        </article>

        <article className={panelClass}>
          <SectionTitle
            eyebrow="Inteligência"
            title="Sugestões operacionais"
            description="Os modelos abaixo ajudam a orientar a escolha do tipo de geração."
          />
          <ul className="mt-3 space-y-3 text-sm leading-6 text-ink/75">
            <li className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">Para declaração, certificado, diploma e aproveitamento, selecione sempre um estudante.</li>
            <li className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">Para pautas trimestrais, semestrais e anuais, indique ano letivo e pelo menos classe ou turma.</li>
            <li className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">Para listas por classe e ano, preencha a classe. Para listas por turma, escolha a turma.</li>
            <li className="rounded-[1rem] border border-ink/10 bg-ink/5 px-3 py-2">Relatórios estatísticos funcionam melhor com o ano letivo definido para produzir contagens mais úteis.</li>
          </ul>
        </article>
      </section>

      <section id="catalog" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Catálogo de geração"
          subtitle="Tipos disponíveis no backend para documentos, relatórios, estatísticas, pautas e listagens."
          snapshot={snapshot.catalog}
          rows={filteredCatalog}
          renderRow={(item: ReportCatalogItem) => (
            <div key={item.key} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{item.label}</p>
                <span className={sideBadge}>
                  {item.scope === "student" ? "Aluno" : "Escola"}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">
                Requisitos: {item.requires.length > 0 ? item.requires.map(humanizeRequirement).join(", ") : "nenhum obrigatório"}
              </p>
              <p className="mt-2 text-xs leading-4 text-ink/50">Chave técnica: {item.key}</p>
            </div>
          )}
        />

        <RecordList
          title="Liderança disponível"
          subtitle="Cargos ativos úteis para relatórios nominais de direção e coordenação."
          snapshot={snapshot.managementAssignments}
          rows={directorRows}
          renderRow={(item: ManagementAssignment) => (
            <div key={item.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{item.teacher_name || "Professor sem nome"}</p>
                <span className={sideBadge}>
                  {item.academic_year_code || "Sem ano letivo"}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{item.role}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {item.classroom_name || item.grade_number ? `Escopo ${item.classroom_name || `Classe ${item.grade_number}`}` : "Escopo escolar"}
              </p>
            </div>
          )}
        />
      </section>

      <section id="history">
        <RecordList
          title="Histórico de relatórios"
          subtitle="Documentos já persistidos e prontos para consulta, impressão ou futura exportação."
          snapshot={snapshot.reports}
          rows={filteredReports.slice(0, 10)}
          renderRow={(item: ReportRecord) => {
            const content = item.content as {
              report_kind?: string;
              metadata?: { academic_year?: string; classroom?: string; grade?: number; period_label?: string };
              student_snapshot?: { name?: string };
            };

            return (
              <div key={item.id} className={panelClass}>
                <div className="flex items-center justify-between gap-3">
                  <Link href={`/reports/${item.id}`} className="font-semibold text-ink underline-offset-2 hover:underline">
                    {item.title}
                  </Link>
                  <span className={sideBadge}>
                    {formatReportType(item.type)}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/70">
                  {content.student_snapshot?.name || "Documento coletivo"} | {content.report_kind || "sem tipo"} 
                </p>
                <p className="mt-1 text-sm leading-6 text-ink/55">
                  {content.metadata?.academic_year || "Sem ano"} · {content.metadata?.classroom || `Classe ${content.metadata?.grade || "-"}`} · {content.metadata?.period_label || item.period || "Sem período"}
                </p>
                <p className="mt-1 text-xs leading-4 text-ink/50">Gerado em {formatDateTime(item.generated_at)}</p>
                <p className="mt-2 text-xs font-semibold text-ink/75 underline-offset-2 hover:underline">
                  <Link href={`/reports/${item.id}`}>Abrir detalhe do documento</Link>
                </p>
              </div>
            );
          }}
        />
      </section>
    </DashboardShell>
  );
}
