import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
import { formatInvoiceStatus, formatPaymentMethod, formatStudentStatus } from "@/lib/labels";
import {
  createInvoice,
  createPayment,
  handleMutationRedirect,
  type Guardian,
  type Invoice,
  type Payment,
  type Student,
  getFinanceSnapshot,
  requireAuthSession,
  updateInvoice,
} from "@/lib/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-PT", { dateStyle: "medium" }).format(new Date(value));
}

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

const panelClass = "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/95 p-4 shadow-[0_18px_50px_rgba(20,33,61,0.08)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_55px_rgba(20,33,61,0.1)]";
const badgeClass = "rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70";
const controlClass = "w-full rounded-[1rem] border border-ink/10 bg-sand px-3 py-2 text-sm text-ink shadow-[inset_0_1px_0_rgba(0,0,0,0.05)] outline-none transition placeholder:text-ink/40 focus:border-ink/30 focus:ring-4 focus:ring-mist";

async function createInvoiceAction(formData: FormData) {
  "use server";

  const result = await createInvoice({
    student: Number(formData.get("student")),
    school: Number(formData.get("school")),
    reference: String(formData.get("reference") || "").trim(),
    description: String(formData.get("description") || "").trim(),
    amount: Number(formData.get("amount") || 0),
    due_date: String(formData.get("due_date") || ""),
    status: String(formData.get("status") || "issued"),
  });

  revalidatePath("/finance");
  await handleMutationRedirect(result, "/finance", "invoice-created", "invoice-error");
}

async function createPaymentAction(formData: FormData) {
  "use server";

  const result = await createPayment({
    invoice: Number(formData.get("invoice")),
    amount: Number(formData.get("amount") || 0),
    payment_date: String(formData.get("payment_date") || ""),
    method: String(formData.get("method") || "cash"),
    reference: String(formData.get("reference") || "").trim(),
    notes: String(formData.get("notes") || "").trim(),
  });

  revalidatePath("/finance");
  await handleMutationRedirect(result, "/finance", "payment-created", "payment-error");
}

async function updateInvoiceStatusAction(formData: FormData) {
  "use server";

  const id = Number(formData.get("id"));
  const status = String(formData.get("status") || "issued");
  const result = await updateInvoice(id, { status });

  revalidatePath("/finance");
  await handleMutationRedirect(result, "/finance", "invoice-updated", "invoice-update-error");
}

export default async function FinancePage({ searchParams }: PageProps) {
  await requireAuthSession("/finance");
  const snapshot = await getFinanceSnapshot();
  const params = (await searchParams) || {};
  const status = Array.isArray(params.status) ? params.status[0] : params.status;
  const invoiceStatus = readParam(params.invoice_status);
  const paymentMethod = readParam(params.payment_method);

  const filteredInvoices = snapshot.invoices.items.filter((item) => {
    if (invoiceStatus && item.status !== invoiceStatus) {
      return false;
    }
    return true;
  });

  const filteredPayments = snapshot.payments.items.filter((item) => {
    if (paymentMethod && item.method !== paymentMethod) {
      return false;
    }
    return true;
  });

  return (
    <DashboardShell
      title="Operações financeiras"
      description="Acompanhamento financeiro escolar entre alunos, responsáveis, faturas e pagamentos."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Receita"
              title="Pulso financeiro"
              description="Visão compacta dos alunos faturados e cobertura de pagamentos."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Faturas</dt>
                <dd>{snapshot.invoices.count} registos de faturas carregados.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Pagamentos</dt>
                <dd>{snapshot.payments.count} eventos de pagamento visíveis.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Encarregados</dt>
                <dd>{snapshot.guardians.count} contactos financeiros registados.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária financeira" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#billing">Faturação</a></li>
              <li><a href="#collections">Cobranças</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      <section className="overflow-hidden rounded-[1.5rem] border border-white/65 bg-[linear-gradient(135deg,rgba(20,33,61,0.95),rgba(32,52,85,0.95))] p-5 text-sand shadow-card shadow-[0_30px_80px_rgba(20,33,61,0.18)]">
        <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-fern/80">Finanças</p>
            <h2 className="mt-3 font-display text-3xl font-bold leading-tight">Pulso financeiro e operação de cobrança.</h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-sand/80">
              Controle as faturas emitidas, pagamentos realizados e contato com responsáveis com o mesmo cuidado visual que o restante do painel.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Faturas</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.invoices.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Pagamentos</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.payments.count}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/30 bg-white/10 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/70">Encarregados</p>
              <p className="mt-2 font-display text-2xl font-semibold">{snapshot.guardians.count}</p>
            </div>
          </div>
        </div>
      </section>
      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_55px_rgba(20,33,61,0.08)]">
        <p className="text-sm text-ink/70">
          Recorte atual — estado: {invoiceStatus || "todas"} · método: {paymentMethod || "todos"}.
        </p>
      </div>

      {status ? (
        <section className={`mt-4 rounded-[1.1rem] border px-4 py-3 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "invoice-created" && "Fatura criada com sucesso."}
          {status === "payment-created" && "Pagamento registado com sucesso."}
          {status === "invoice-updated" && "Fatura atualizada com sucesso."}
          {status === "invoice-error" && "Não foi possível criar a fatura."}
          {status === "payment-error" && "Não foi possível registar o pagamento."}
          {status === "invoice-update-error" && "Não foi possível atualizar a fatura."}
          {status === "session-expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <div className="mt-6 overflow-hidden rounded-[1.25rem] border border-white/60 bg-white/95 p-4 shadow-[0_18px_55px_rgba(20,33,61,0.08)]">
        <FilterBar
        fields={[
          {
            name: "invoice_status",
            label: "Fatura",
            value: invoiceStatus,
            options: Array.from(new Set(snapshot.invoices.items.map((item) => item.status))).map((item) => ({
              value: item,
              label: formatInvoiceStatus(item),
            })),
          },
          {
            name: "payment_method",
            label: "Pagamento",
            value: paymentMethod,
            options: Array.from(new Set(snapshot.payments.items.map((item) => item.method))).map((item) => ({
              value: item,
              label: formatPaymentMethod(item),
            })),
          },
        ]}
        />
      </div>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className={panelClass}>
          <SectionTitle
            eyebrow="Criar"
            title="Emitir fatura"
            description="Registe um novo encargo financeiro para um aluno."
          />
          <form action={createInvoiceAction} className="mt-3 grid gap-3">
            <select name="student" required className={controlClass}>
              {snapshot.students.items.map((student) => (
                <option key={student.id} value={student.id}>{student.name}</option>
              ))}
            </select>
            <select name="school" required className={controlClass}>
              {snapshot.schools.items.map((school) => (
                <option key={school.id} value={school.id}>{school.name}</option>
              ))}
            </select>
            <input name="reference" required placeholder="Referência" className={controlClass} />
            <input name="description" required placeholder="Descrição" className={controlClass} />
            <input name="amount" type="number" step="0.01" min="0" required placeholder="Montante" className={controlClass} />
            <input name="due_date" type="date" required className={controlClass} />
            <select name="status" defaultValue="issued" className={controlClass}>
              <option value="draft">Rascunho</option>
              <option value="issued">Emitida</option>
              <option value="paid">Paga</option>
              <option value="overdue">Em atraso</option>
            </select>
            <SubmitButton idleLabel="Emitir fatura" pendingLabel="A emitir fatura..." className="w-full px-4 py-3" />
          </form>
        </article>

        <article className={panelClass}>
          <SectionTitle
            eyebrow="Criar"
            title="Registar pagamento"
            description="Registe um pagamento para uma fatura existente."
          />
          <form action={createPaymentAction} className="mt-3 grid gap-3">
            <select name="invoice" required className={controlClass}>
              {snapshot.invoices.items.map((invoice) => (
                <option key={invoice.id} value={invoice.id}>{invoice.reference} | {invoice.student_name}</option>
              ))}
            </select>
            <input name="amount" type="number" step="0.01" min="0" required placeholder="Montante pago" className={controlClass} />
            <input name="payment_date" type="date" required className={controlClass} />
            <select name="method" defaultValue="cash" className={controlClass}>
              <option value="cash">Numerário</option>
              <option value="bank_transfer">Transferência bancária</option>
              <option value="mobile_money">Carteira móvel</option>
              <option value="card">Cartão</option>
            </select>
            <input name="reference" placeholder="Referência do pagamento" className={controlClass} />
            <input name="notes" placeholder="Observações" className={controlClass} />
            <SubmitButton idleLabel="Registar pagamento" pendingLabel="A registar pagamento..." className="w-full px-4 py-3" />
          </form>
        </article>
      </section>

      <section id="billing" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Alunos"
          subtitle="Base de alunos faturáveis no recorte atual."
          snapshot={snapshot.students}
          rows={snapshot.students.items.slice(0, 8)}
          renderRow={(student: Student) => (
            <div key={student.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{student.name}</p>
                <span className={badgeClass}>{formatStudentStatus(student.status)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">Classe {student.grade} | {student.education_level}</p>
            </div>
          )}
        />
        <RecordList
          title="Faturas"
          subtitle="Registos emitidos, pendentes, pagos ou em atraso."
          snapshot={snapshot.invoices}
          rows={filteredInvoices.slice(0, 8)}
          renderRow={(invoice: Invoice) => (
            <div key={invoice.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{invoice.reference}</p>
                <span className={badgeClass}>{formatInvoiceStatus(invoice.status)}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{invoice.student_name}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">
                {invoice.amount} · Vencimento {formatDate(invoice.due_date)}
              </p>
              <form action={updateInvoiceStatusAction} className="mt-3 flex flex-wrap gap-2">
                <input type="hidden" name="id" value={invoice.id} />
                <select name="status" defaultValue={invoice.status} className="rounded-[1rem] border border-ink/10 bg-sand px-3 py-1.5 text-xs text-ink">
                  <option value="draft">Rascunho</option>
                  <option value="issued">Emitida</option>
                  <option value="paid">Paga</option>
                  <option value="overdue">Em atraso</option>
                  <option value="cancelled">Cancelada</option>
                </select>
                <button type="submit" className="rounded-full border border-ink/10 bg-sand px-3 py-1.5 text-[11px] font-semibold text-ink transition hover:border-ink/30 hover:bg-white">
                  Atualizar
                </button>
              </form>
            </div>
          )}
        />
      </section>

      <section id="collections" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Pagamentos"
          subtitle="Pagamentos recebidos associados a faturas."
          snapshot={snapshot.payments}
          rows={filteredPayments.slice(0, 8)}
          renderRow={(payment: Payment) => (
            <div key={payment.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{payment.invoice_reference}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  {payment.amount}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{formatPaymentMethod(payment.method)}</p>
              <p className="mt-1 text-sm leading-6 text-ink/55">{formatDate(payment.payment_date)} · {payment.reference || "Sem referência de pagamento"}</p>
            </div>
          )}
        />
        <RecordList
          title="Encarregados"
          subtitle="Contactos prioritários para faturação e acompanhamento."
          snapshot={snapshot.guardians}
          rows={snapshot.guardians.items.slice(0, 8)}
          renderRow={(guardian: Guardian) => (
            <div key={guardian.id} className={panelClass}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{guardian.name}</p>
                <span className={badgeClass}>{guardian.relationship || "Parentesco não definido"}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink/70">{guardian.phone || guardian.email || "Sem contacto financeiro"}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
