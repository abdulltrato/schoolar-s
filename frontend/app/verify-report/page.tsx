import Link from "next/link";
import { getReportVerification } from "@/lib/api";

function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

function formatDateTime(value?: string) {
  if (!value) {
    return "Sem data";
  }
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "full",
    timeStyle: "short",
  }).format(new Date(value));
}

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

export default async function VerifyReportPage({ searchParams }: PageProps) {
  const params = (await searchParams) || {};
  const code = readParam(params.code);
  const hash = readParam(params.hash);
  const response = code ? await getReportVerification(code, hash || undefined) : null;
  const payload = response?.data;
  const valid = Boolean(response?.ok && payload?.valid);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(217,108,6,0.14),transparent_24%),linear-gradient(180deg,#f7f3e9_0%,#fbf8f2_100%)] px-4 py-8 text-ink">
      <div className="mx-auto max-w-3xl space-y-4">
        <header className="rounded-[1.2rem] border border-ink/10 bg-white/95 p-6 shadow-card">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-ink/55">Validação documental</p>
          <h1 className="mt-2 font-display text-3xl font-bold text-ink">Verificação de autenticidade</h1>
          <p className="mt-2 text-sm leading-6 text-ink/72">
            Esta página valida se uma declaração, certificado, diploma, pauta ou relatório foi emitido pelo sistema e se a assinatura continua íntegra.
          </p>
          <form className="mt-5 grid gap-3 rounded-[1rem] border border-ink/10 bg-sand/60 p-4 sm:grid-cols-[1fr_1fr_auto]">
            <label className="block">
              <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Código</span>
              <input
                name="code"
                defaultValue={code}
                placeholder="RPT-XXXXXX"
                className="mt-1 w-full rounded-md border border-ink/10 bg-white px-3 py-2 text-sm text-ink"
              />
            </label>
            <label className="block">
              <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Assinatura</span>
              <input
                name="hash"
                defaultValue={hash}
                placeholder="Hash SHA-256"
                className="mt-1 w-full rounded-md border border-ink/10 bg-white px-3 py-2 text-sm text-ink"
              />
            </label>
            <div className="flex items-end">
              <button
                type="submit"
                className="w-full rounded-full bg-ink px-4 py-2 text-sm font-semibold text-sand sm:w-auto"
              >
                Validar
              </button>
            </div>
          </form>
        </header>

        {!code ? (
          <section className="rounded-[1.2rem] border border-ember/20 bg-white/95 p-6 shadow-card">
            <p className="text-sm text-ember">Código de verificação em falta. Use um link completo de validação ou forneça `code` e `hash` na URL.</p>
          </section>
        ) : (
          <section className={`rounded-[1.2rem] border bg-white/95 p-6 shadow-card ${valid ? "border-fern/20" : "border-ember/20"}`}>
            <div className={`rounded-[0.9rem] px-4 py-3 text-sm ${valid ? "bg-fern/10 text-fern" : "bg-ember/10 text-ember"}`}>
              {valid ? "Documento autêntico e assinatura válida." : payload?.reason || "Não foi possível validar o documento."}
            </div>

            <dl className="mt-4 grid gap-3 sm:grid-cols-2">
              <div className="rounded-[0.9rem] border border-ink/10 bg-sand px-4 py-3">
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Código</dt>
                <dd className="mt-1 text-sm text-ink/75">{payload?.verification_code || code}</dd>
              </div>
              <div className="rounded-[0.9rem] border border-ink/10 bg-sand px-4 py-3">
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Estado</dt>
                <dd className="mt-1 text-sm text-ink/75">{valid ? "Autêntico" : "Inválido"}</dd>
              </div>
              <div className="rounded-[0.9rem] border border-ink/10 bg-sand px-4 py-3">
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Título</dt>
                <dd className="mt-1 text-sm text-ink/75">{payload?.title || "Não disponível"}</dd>
              </div>
              <div className="rounded-[0.9rem] border border-ink/10 bg-sand px-4 py-3">
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Tipo</dt>
                <dd className="mt-1 text-sm text-ink/75">{payload?.type || "Não disponível"}</dd>
              </div>
              <div className="rounded-[0.9rem] border border-ink/10 bg-sand px-4 py-3">
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Estudante</dt>
                <dd className="mt-1 text-sm text-ink/75">{payload?.student_name || "Documento coletivo"}</dd>
              </div>
              <div className="rounded-[0.9rem] border border-ink/10 bg-sand px-4 py-3">
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Gerado em</dt>
                <dd className="mt-1 text-sm text-ink/75">{formatDateTime(payload?.generated_at)}</dd>
              </div>
            </dl>

            <div className="mt-4 rounded-[0.9rem] border border-ink/10 bg-white px-4 py-3">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Assinatura</p>
              <p className="mt-1 break-all text-xs leading-5 text-ink/70">{payload?.verification_hash || hash || "Não fornecida"}</p>
            </div>
          </section>
        )}

        <div className="text-sm text-ink/70">
          <Link href="/login" className="font-semibold underline underline-offset-2">Entrar na plataforma</Link>
        </div>
      </div>
    </main>
  );
}
