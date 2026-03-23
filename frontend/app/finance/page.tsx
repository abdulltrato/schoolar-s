import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { DashboardShell } from "@/components/dashboard-shell";
import { FilterBar } from "@/components/filter-bar";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { SubmitButton } from "@/components/submit-button";
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
      title="Finance Operations"
      description="School-level financial follow-up across students, guardians, invoices, and payments."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Revenue"
              title="Financial Pulse"
              description="Compact view of billed students and payment coverage."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Invoices</dt>
                <dd>{snapshot.invoices.count} invoice records loaded.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Payments</dt>
                <dd>{snapshot.payments.count} payment events visible.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Guardians</dt>
                <dd>{snapshot.guardians.count} guardian finance contacts.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Finance secondary navigation" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Sections</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#billing">Billing</a></li>
              <li><a href="#collections">Collections</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "invoice-created" && "Invoice created successfully."}
          {status === "payment-created" && "Payment created successfully."}
          {status === "invoice-updated" && "Invoice updated successfully."}
          {status === "invoice-error" && "Could not create the invoice."}
          {status === "payment-error" && "Could not create the payment."}
          {status === "invoice-update-error" && "Could not update the invoice."}
          {status === "session-expired" && "Your session expired. Sign in again to continue."}
        </section>
      ) : null}

      <FilterBar
        fields={[
          {
            name: "invoice_status",
            label: "Invoice",
            value: invoiceStatus,
            options: Array.from(new Set(snapshot.invoices.items.map((item) => item.status))).map((item) => ({
              value: item,
              label: item,
            })),
          },
          {
            name: "payment_method",
            label: "Payment",
            value: paymentMethod,
            options: Array.from(new Set(snapshot.payments.items.map((item) => item.method))).map((item) => ({
              value: item,
              label: item,
            })),
          },
        ]}
      />

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Create"
            title="Issue Invoice"
            description="Register a new financial charge against a student."
          />
          <form action={createInvoiceAction} className="mt-3 grid gap-2">
            <select name="student" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.students.items.map((student) => (
                <option key={student.id} value={student.id}>{student.name}</option>
              ))}
            </select>
            <select name="school" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.schools.items.map((school) => (
                <option key={school.id} value={school.id}>{school.name}</option>
              ))}
            </select>
            <input name="reference" required placeholder="Reference" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="description" required placeholder="Description" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="amount" type="number" step="0.01" min="0" required placeholder="Amount" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="due_date" type="date" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <select name="status" defaultValue="issued" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="draft">Draft</option>
              <option value="issued">Issued</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
            </select>
            <SubmitButton idleLabel="Create invoice" pendingLabel="Creating invoice..." />
          </form>
        </article>

        <article className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-3 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Create"
            title="Register Payment"
            description="Capture a payment event against an existing invoice."
          />
          <form action={createPaymentAction} className="mt-3 grid gap-2">
            <select name="invoice" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              {snapshot.invoices.items.map((invoice) => (
                <option key={invoice.id} value={invoice.id}>{invoice.reference} | {invoice.student_name}</option>
              ))}
            </select>
            <input name="amount" type="number" step="0.01" min="0" required placeholder="Paid amount" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="payment_date" type="date" required className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <select name="method" defaultValue="cash" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink">
              <option value="cash">Cash</option>
              <option value="bank_transfer">Bank transfer</option>
              <option value="mobile_money">Mobile money</option>
              <option value="card">Card</option>
            </select>
            <input name="reference" placeholder="Payment reference" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <input name="notes" placeholder="Notes" className="rounded-md border border-ink/10 bg-sand px-2.5 py-2 text-sm text-ink" />
            <SubmitButton idleLabel="Register payment" pendingLabel="Registering payment..." />
          </form>
        </article>
      </section>

      <section id="billing" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Students"
          subtitle="Base of billable learners within the current scope."
          snapshot={snapshot.students}
          rows={snapshot.students.items.slice(0, 8)}
          renderRow={(student: Student) => (
            <div key={student.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{student.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">Grade {student.grade} | {student.education_level}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">Status: {student.status}</p>
            </div>
          )}
        />
        <RecordList
          title="Invoices"
          subtitle="Issued, pending, paid, or overdue billing records."
          snapshot={snapshot.invoices}
          rows={filteredInvoices.slice(0, 8)}
          renderRow={(invoice: Invoice) => (
            <div key={invoice.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{invoice.reference}</p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {invoice.status}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{invoice.student_name}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {invoice.amount} | Due {formatDate(invoice.due_date)}
              </p>
              <form action={updateInvoiceStatusAction} className="mt-2 flex gap-2">
                <input type="hidden" name="id" value={invoice.id} />
                <select name="status" defaultValue={invoice.status} className="rounded-md border border-ink/10 bg-sand px-2 py-1 text-xs text-ink">
                  <option value="draft">Draft</option>
                  <option value="issued">Issued</option>
                  <option value="paid">Paid</option>
                  <option value="overdue">Overdue</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                <button type="submit" className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink">
                  Update
                </button>
              </form>
            </div>
          )}
        />
      </section>

      <section id="collections" className="grid gap-4 lg:grid-cols-2">
        <RecordList
          title="Payments"
          subtitle="Received payments tied to invoice references."
          snapshot={snapshot.payments}
          rows={filteredPayments.slice(0, 8)}
          renderRow={(payment: Payment) => (
            <div key={payment.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{payment.invoice_reference}</p>
                <span className="rounded-full bg-fern/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-fern">
                  {payment.amount}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{payment.method}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{formatDate(payment.payment_date)} | {payment.reference || "No payment ref"}</p>
            </div>
          )}
        />
        <RecordList
          title="Guardians"
          subtitle="Primary family contacts supporting billing and follow-up."
          snapshot={snapshot.guardians}
          rows={snapshot.guardians.items.slice(0, 8)}
          renderRow={(guardian: Guardian) => (
            <div key={guardian.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <p className="font-semibold text-ink">{guardian.name}</p>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{guardian.relationship || "Relationship not set"}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">{guardian.phone || guardian.email || "No finance contact detail"}</p>
            </div>
          )}
        />
      </section>
    </DashboardShell>
  );
}
