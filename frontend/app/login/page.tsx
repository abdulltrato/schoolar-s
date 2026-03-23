import { redirect } from "next/navigation";
import { loginAction } from "@/app/auth/actions";
import { getAuthSession } from "@/lib/api";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export default async function LoginPage({ searchParams }: PageProps) {
  const session = await getAuthSession();
  const params = (await searchParams) || {};
  const error = readParam(params.error);
  const nextPath = readParam(params.next) || "/";

  if (session.authenticated) {
    redirect(nextPath);
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(217,108,6,0.16),transparent_28%),radial-gradient(circle_at_top_right,rgba(60,122,87,0.12),transparent_24%),linear-gradient(180deg,#f7f3e9_0%,#fbf8f2_100%)] px-4 py-10 text-ink">
      <div className="mx-auto max-w-md rounded-[1.25rem] border border-ink/10 bg-white/95 p-6 shadow-card backdrop-blur">
        <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ember">Schoolar-S</p>
        <h1 className="mt-2 font-display text-2xl font-bold">Entrar</h1>
        <p className="mt-2 text-sm leading-5 text-ink/70">
          Use uma conta do backend. O frontend vai espelhar a sessão em cookie e resolver o seu papel a partir do perfil da plataforma.
        </p>

        {error ? (
          <div className="mt-4 rounded-[0.9rem] border border-ember/20 bg-ember/10 px-3 py-2 text-sm text-ember">
            {error === "session_setup_failed" && "A autenticação ocorreu, mas o cookie de sessão do backend não foi emitido."}
            {error === "session_expired" && "A sua sessão expirou. Entre novamente para continuar."}
            {error !== "session_setup_failed" && error !== "session_expired" && "Nome de utilizador ou palavra-passe inválidos."}
          </div>
        ) : null}

        <form action={loginAction} className="mt-5 grid gap-3">
          <input type="hidden" name="next" value={nextPath} />
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Nome de utilizador</span>
            <input
              name="username"
              required
              autoComplete="username"
              className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-3 py-2 text-sm text-ink"
            />
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Palavra-passe</span>
            <input
              name="password"
              type="password"
              required
              autoComplete="current-password"
              className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-3 py-2 text-sm text-ink"
            />
          </label>
          <button type="submit" className="mt-2 rounded-full bg-ink px-4 py-2 text-sm font-semibold text-sand">
            Entrar
          </button>
        </form>
      </div>
    </main>
  );
}
