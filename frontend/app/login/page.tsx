import { redirect } from "next/navigation";
import { loginAction } from "@/app/auth/actions";
import { SubmitButton } from "@/components/submit-button";
import { getAuthSession } from "@/lib/api";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

// Normaliza query param (usa primeiro valor).
function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export default async function LoginPage({ searchParams }: PageProps) {
  // Se já autenticado, redireciona para next (ou /).
  const session = await getAuthSession();
  const params = (await searchParams) || {};
  const error = readParam(params.error);
  const nextPath = readParam(params.next) || "/";

  if (session.authenticated) {
    redirect(nextPath);
  }

  return (
    <main className="min-h-screen bg-white px-4 py-10 text-ink sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-xl flex-col items-center justify-center gap-8">
        <div className="flex flex-col items-center gap-2 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-ink/60">Schoolar-S</p>
          <h1 className="font-display text-3xl font-bold tracking-tight">Iniciar sessão</h1>
          <p className="text-sm text-ink/65">
            Use as credenciais institucionais para entrar. Nada mais é mostrado nesta página.
          </p>
        </div>

        {error ? (
          <div className="w-full rounded-xl border border-ember/30 bg-ember/10 px-4 py-3 text-sm leading-6 text-ember">
            {error === "session_setup_failed" && "A autenticação ocorreu, mas o cookie de sessão do backend não foi emitido."}
            {error === "session_expired" && "A sua sessão expirou. Entre novamente para continuar."}
            {error !== "session_setup_failed" && error !== "session_expired" && "Nome de utilizador ou palavra-passe inválidos."}
          </div>
        ) : null}

        <section className="w-full rounded-2xl border border-ink/10 bg-white p-6 shadow-card sm:p-8">
          <form action={loginAction} className="grid gap-5">
            <input type="hidden" name="next" value={nextPath} />
            <label className="block">
              <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">Nome de utilizador</span>
              <input
                name="username"
                required
                autoComplete="username"
                placeholder="ex.: admin"
                className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/40 focus:ring-4 focus:ring-mist"
              />
            </label>
            <label className="block">
              <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">Palavra-passe</span>
              <input
                name="password"
                type="password"
                required
                autoComplete="current-password"
                placeholder="Introduza a sua palavra-passe"
                className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/40 focus:ring-4 focus:ring-mist"
              />
            </label>

            <SubmitButton
              idleLabel="Entrar"
              pendingLabel="A validar acesso..."
              className="mt-2 w-full px-5 py-3 transition hover:bg-[#0e1932] focus:outline-none focus:ring-4 focus:ring-mist"
            />
          </form>
        </section>
      </div>
    </main>
  );
}
