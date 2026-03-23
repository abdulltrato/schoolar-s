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
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Resumo"
              title="Motor documental"
              description="A consola une documentos individuais, listas operacionais e pautas com base no backend."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Modelos</dt>
                <dd>{snapshot.catalog.count} tipos de geração disponíveis.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Relatórios</dt>
                <dd>{snapshot.reports.count} documentos já persistidos.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Base escolar</dt>
                <dd>{snapshot.students.count} estudantes, {snapshot.teachers.count} professores e {snapshot.classrooms.count} turmas carregadas.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária de relatórios" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#generator">Gerador</a></li>
              <li><a href="#catalog">Catálogo</a></li>
              <li><a href="#history">Histórico</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "report-generated" && "Relatório gerado e guardado com sucesso."}
          {status === "report-error" && "Não foi possível gerar o relatório pedido."}
        </section>
      ) : null}

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

      <section id="generator" className="grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Gerar"
            title="Orquestrador de documentos"
            description="Escolha o tipo de saída e o contexto académico. O backend decide a estrutura e persiste o documento."
          />
          <form action={generateReportAction} className="mt-3 grid gap-2 md:grid-cols-2">
            <select name="report_kind" defaultValue={reportKind} required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Selecionar tipo de geração</option>
              {snapshot.catalog.items.map((item) => (
                <option key={item.key} value={item.key}>{item.label}</option>
              ))}
            </select>
            <input name="title" placeholder="Título opcional" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <select name="student" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Sem estudante específico</option>
              {snapshot.students.items.map((item) => (
                <option key={item.id} value={item.id}>{item.name} | Classe {item.grade}</option>
              ))}
            </select>
            <select name="academic_year" defaultValue={snapshot.academicYears.items[0]?.id ? String(snapshot.academicYears.items[0].id) : ""} className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Sem ano letivo</option>
              {snapshot.academicYears.items.map((item) => (
                <option key={item.id} value={item.id}>{item.code}</option>
              ))}
            </select>
            <select name="grade" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Sem classe específica</option>
              {snapshot.grades.items.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
            <select name="classroom" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Sem turma específica</option>
              {snapshot.classrooms.items.map((item) => (
                <option key={item.id} value={item.id}>{item.name} | {item.academic_year}</option>
              ))}
            </select>
            <select name="period_scope" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Escopo automático</option>
              <option value="quarterly">Trimestral</option>
              <option value="semester">Semestral</option>
              <option value="annual">Anual</option>
            </select>
            <select name="period_order" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="">Período automático</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
            <div className="md:col-span-2">
              <SubmitButton idleLabel="Gerar e guardar relatório" pendingLabel="A gerar relatório..." />
            </div>
          </form>
        </article>

        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Inteligência"
            title="Sugestões operacionais"
            description="Os modelos abaixo ajudam a orientar a escolha do tipo de geração."
          />
          <ul className="mt-3 space-y-2 text-sm leading-5 text-ink/75">
            <li>Para declaração, certificado, diploma e aproveitamento, selecione sempre um estudante.</li>
            <li>Para pautas trimestrais, semestrais e anuais, indique ano letivo e pelo menos classe ou turma.</li>
            <li>Para listas por classe e ano, preencha a classe. Para listas por turma, escolha a turma.</li>
            <li>Relatórios estatísticos funcionam melhor com o ano letivo definido para produzir contagens mais úteis.</li>
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
            <div key={item.key} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{item.label}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {item.scope === "student" ? "Aluno" : "Escola"}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/55">
                Requisitos: {item.requires.length > 0 ? item.requires.map(humanizeRequirement).join(", ") : "nenhum obrigatório"}
              </p>
              <p className="mt-1 text-xs leading-4 text-ink/50">Chave técnica: {item.key}</p>
            </div>
          )}
        />

        <RecordList
          title="Liderança disponível"
          subtitle="Cargos ativos úteis para relatórios nominais de direção e coordenação."
          snapshot={snapshot.managementAssignments}
          rows={directorRows}
          renderRow={(item: ManagementAssignment) => (
            <div key={item.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{item.teacher_name || "Professor sem nome"}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{item.role} | {item.academic_year_code || "Sem ano letivo"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
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
              <div key={item.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <Link href={`/reports/${item.id}`} className="font-semibold text-ink underline-offset-2 hover:underline">
                    {item.title}
                  </Link>
                  <span className="rounded-full bg-ember/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ember">
                    {formatReportType(item.type)}
                  </span>
                </div>
                <p className="mt-1.5 text-sm leading-5 text-ink/70">
                  {content.student_snapshot?.name || "Documento coletivo"} | {content.report_kind || "sem tipo"} 
                </p>
                <p className="mt-1 text-sm leading-5 text-ink/55">
                  {content.metadata?.academic_year || "Sem ano"} | {content.metadata?.classroom || `Classe ${content.metadata?.grade || "-"}`} | {content.metadata?.period_label || item.period || "Sem período"}
                </p>
                <p className="mt-1 text-xs leading-4 text-ink/50">Gerado em {formatDateTime(item.generated_at)}</p>
                <p className="mt-2">
                  <Link href={`/reports/${item.id}`} className="text-xs font-semibold text-ink/75 underline-offset-2 hover:underline">
                    Abrir detalhe do documento
                  </Link>
                </p>
              </div>
            );
          }}
        />
      </section>
    </DashboardShell>
  );
}
