import { redirect } from "next/navigation";
import { changePasswordLoginAction, loginAction } from "@/app/auth/actions";
import { SubmitButton } from "@/components/submit-button";
import { getAuthSession } from "@/lib/api";
import { getLocale, t } from "@/lib/locale";

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
  const locale = await getLocale();
  const params = (await searchParams) || {};
  const error = readParam(params.error);
  const detail = readParam(params.detail);
  const nextPath = readParam(params.next) || "/";
  const mode = readParam(params.mode) === "change" ? "change" : "login";

  if (session.authenticated) {
    redirect(nextPath);
  }

  return (
    <main className="min-h-screen bg-white px-4 py-10 text-ink sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-xl flex-col items-center justify-center gap-8">
        <div className="flex flex-col items-center gap-2 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-ink/60">{t(locale, "brand")}</p>
          <h1 className="font-display text-3xl font-bold tracking-tight">
            {mode === "change" ? t(locale, "changeTitle") : t(locale, "loginTitle")}
          </h1>
          <p className="text-sm text-ink/65">
            {mode === "change"
              ? t(locale, "changeSubtitle")
              : t(locale, "loginSubtitle")}
          </p>
        </div>

        {error ? (
          <div className="w-full rounded-xl border border-ember/30 bg-ember/10 px-4 py-3 text-sm leading-6 text-ember">
            {error === "session_setup_failed" && "A autenticação ocorreu, mas o cookie de sessão do backend não foi emitido."}
            {error === "session_expired" && "A sua sessão expirou. Entre novamente para continuar."}
            {error === "change_failed" && (detail ? decodeURIComponent(detail) : "Não foi possível alterar a palavra-passe.")}
            {error !== "session_setup_failed" && error !== "session_expired" && error !== "change_failed" && "Nome de utilizador ou palavra-passe inválidos."}
          </div>
        ) : null}

        <section className="w-full rounded-2xl border border-ink/10 bg-white p-6 shadow-card sm:p-8">
          <div className="mb-4 flex gap-2">
            <a
              href={`/login?mode=login&next=${encodeURIComponent(nextPath)}`}
              className={`rounded-full px-3 py-2 text-xs font-semibold ${
                mode === "login" ? "bg-ink text-sand" : "border border-ink/10 text-ink"
              }`}
            >
              Entrar
            </a>
            <a
              href={`/login?mode=change&next=${encodeURIComponent(nextPath)}`}
              className={`rounded-full px-3 py-2 text-xs font-semibold ${
                mode === "change" ? "bg-ink text-sand" : "border border-ink/10 text-ink"
              }`}
            >
              Alterar palavra-passe
            </a>
          </div>

          {mode === "login" ? (
            <form action={loginAction} className="grid gap-5">
              <input type="hidden" name="next" value={nextPath} />
              <label className="block">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                  {t(locale, "username")}
                </span>
                <input
                  name="username"
                  required
                  autoComplete="username"
                  placeholder="ex.: admin"
                  className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/40 focus:ring-4 focus:ring-mist"
                />
              </label>
              <label className="block">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                  {t(locale, "password")}
                </span>
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
                idleLabel={t(locale, "loginButton")}
                pendingLabel="A validar acesso..."
                className="mt-2 w-full px-5 py-3 transition hover:bg-[#0e1932] focus:outline-none focus:ring-4 focus:ring-mist"
              />
            </form>
          ) : (
            <form action={changePasswordLoginAction} className="grid gap-5">
              <input type="hidden" name="next" value={nextPath} />
              <label className="block">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                  {t(locale, "username")}
                </span>
                <input
                  name="username"
                  required
                  autoComplete="username"
                  placeholder="ex.: admin"
                  className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/40 focus:ring-4 focus:ring-mist"
                />
              </label>
              <label className="block">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                  {t(locale, "passwordCurrent")}
                </span>
                <input
                  name="old_password"
                  type="password"
                  required
                  autoComplete="current-password"
                  placeholder="Digite a senha atual"
                  className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/40 focus:ring-4 focus:ring-mist"
                />
              </label>
              <label className="block">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                  {t(locale, "passwordNew")}
                </span>
                <input
                  name="new_password"
                  type="password"
                  required
                  autoComplete="new-password"
                  placeholder="Defina a nova senha"
                  className="mt-2 w-full rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/40 focus:ring-4 focus:ring-mist"
                />
              </label>

              <SubmitButton
                idleLabel={t(locale, "changeButton")}
                pendingLabel="A validar e atualizar..."
                className="mt-2 w-full px-5 py-3 transition hover:bg-[#0e1932] focus:outline-none focus:ring-4 focus:ring-mist"
              />
            </form>
          )}
        </section>
      </div>
    </main>
  );
}
