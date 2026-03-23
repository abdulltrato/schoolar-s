import { redirect } from "next/navigation";
import { loginAction } from "@/app/auth/actions";
import { SubmitButton } from "@/components/submit-button";
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
    <main className="relative min-h-screen overflow-hidden bg-[linear-gradient(135deg,#0f1a31_0%,#14213d_48%,#203455_100%)] px-4 py-6 text-ink sm:px-6 lg:px-8">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(217,108,6,0.24),transparent_24%),radial-gradient(circle_at_78%_18%,rgba(215,227,239,0.18),transparent_18%),radial-gradient(circle_at_bottom_right,rgba(60,122,87,0.2),transparent_26%)]"
      />
      <div
        aria-hidden
        className="animate-drift-slow pointer-events-none absolute left-[-6rem] top-16 h-48 w-48 rounded-full bg-ember/20 blur-3xl"
      />
      <div
        aria-hidden
        className="animate-drift-delayed pointer-events-none absolute bottom-10 right-[-5rem] h-56 w-56 rounded-full bg-fern/20 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-y-0 left-[8%] hidden w-px bg-white/10 lg:block"
      />

      <div className="relative mx-auto grid min-h-[calc(100vh-3rem)] max-w-6xl items-center gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/8 p-6 text-sand shadow-card backdrop-blur sm:p-8 lg:p-10">
          <div
            aria-hidden
            className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,rgba(217,108,6,0.95),rgba(247,243,233,0.8),rgba(60,122,87,0.9))]"
          />
          <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-sand/70">Schoolar-S</p>
          <h1 className="mt-5 max-w-xl font-display text-4xl font-bold leading-tight sm:text-5xl">
            Acesso executivo para a operação escolar.
          </h1>
          <p className="mt-5 max-w-lg text-sm leading-6 text-sand/74 sm:text-base">
            Entre para gerir currículo, avaliação, finanças e comunicação numa interface mais clara, rápida e orientada
            à leitura operacional.
          </p>

          <div className="mt-8 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-3 py-2 text-xs text-sand/80">
            <span className="h-2 w-2 rounded-full bg-emerald-300 shadow-[0_0_14px_rgba(110,231,183,0.9)]" />
            Sessão institucional com resolução automática de perfil
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1.2rem] border border-white/10 bg-white/8 p-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-sand/55">Módulos</p>
              <p className="mt-2 font-display text-3xl font-bold text-white">10</p>
              <p className="mt-2 text-sm leading-5 text-sand/70">Áreas funcionais integradas numa única navegação.</p>
            </div>
            <div className="rounded-[1.2rem] border border-white/10 bg-white/8 p-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-sand/55">Fluxo</p>
              <p className="mt-2 font-display text-3xl font-bold text-white">1</p>
              <p className="mt-2 text-sm leading-5 text-sand/70">Sessão centralizada com espelhamento por cookie.</p>
            </div>
            <div className="rounded-[1.2rem] border border-white/10 bg-white/8 p-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-sand/55">Perfis</p>
              <p className="mt-2 font-display text-3xl font-bold text-white">RBAC</p>
              <p className="mt-2 text-sm leading-5 text-sand/70">O acesso é resolvido automaticamente a partir do perfil.</p>
            </div>
          </div>

          <div className="mt-8 grid gap-4 border-t border-white/10 pt-6 sm:grid-cols-2">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-ember">Panorama</p>
              <p className="mt-2 text-sm leading-6 text-sand/74">
                Painel concebido para reduzir ruído visual e acelerar leitura de contexto em desktop e mobile.
              </p>
            </div>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-ember">Autenticação</p>
              <p className="mt-2 text-sm leading-6 text-sand/74">
                Use a mesma conta do backend. O frontend apenas propaga a sessão e respeita o papel já configurado.
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-2 text-sm text-sand/72 sm:grid-cols-2">
            <p className="rounded-[1rem] border border-white/10 bg-black/10 px-4 py-3">Leitura rápida dos módulos sem ruído visual excessivo.</p>
            <p className="rounded-[1rem] border border-white/10 bg-black/10 px-4 py-3">Comportamento consistente em telas grandes e dispositivos móveis.</p>
          </div>
        </section>

        <section className="relative overflow-hidden rounded-[2rem] border border-ink/10 bg-[linear-gradient(180deg,rgba(247,243,233,0.98)_0%,rgba(255,255,255,0.96)_100%)] p-6 shadow-card backdrop-blur sm:p-8">
          <div
            aria-hidden
            className="absolute inset-x-6 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(20,33,61,0.25),transparent)]"
          />
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-ember">Sessão segura</p>
              <h2 className="mt-3 font-display text-3xl font-bold tracking-tight text-ink">Entrar na plataforma</h2>
            </div>
            <div className="rounded-full border border-fern/20 bg-fern/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-fern">
              Backend ativo
            </div>
          </div>

          <p className="mt-4 max-w-md text-sm leading-6 text-ink/68">
            Informe as credenciais da sua conta institucional para abrir a área correspondente ao seu perfil.
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[1rem] border border-ink/10 bg-white/70 px-3 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/45">Ambiente</p>
              <p className="mt-1 text-sm font-semibold text-ink">Operacional</p>
            </div>
            <div className="rounded-[1rem] border border-ink/10 bg-white/70 px-3 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/45">Sessão</p>
              <p className="mt-1 text-sm font-semibold text-ink">Cookie seguro</p>
            </div>
            <div className="rounded-[1rem] border border-ink/10 bg-white/70 px-3 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/45">Destino</p>
              <p className="mt-1 truncate text-sm font-semibold text-ink">{nextPath}</p>
            </div>
          </div>

          {error ? (
            <div className="mt-6 rounded-[1.1rem] border border-ember/20 bg-ember/10 px-4 py-3 text-sm leading-6 text-ember">
              {error === "session_setup_failed" && "A autenticação ocorreu, mas o cookie de sessão do backend não foi emitido."}
              {error === "session_expired" && "A sua sessão expirou. Entre novamente para continuar."}
              {error !== "session_setup_failed" && error !== "session_expired" && "Nome de utilizador ou palavra-passe inválidos."}
            </div>
          ) : null}

          <form action={loginAction} className="mt-8 grid gap-4">
            <input type="hidden" name="next" value={nextPath} />
            <label className="block">
              <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/58">Nome de utilizador</span>
              <input
                name="username"
                required
                autoComplete="username"
                placeholder="ex.: admin"
                className="mt-2 w-full rounded-[1rem] border border-ink/10 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/30 focus:ring-4 focus:ring-mist"
              />
            </label>
            <label className="block">
              <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/58">Palavra-passe</span>
              <input
                name="password"
                type="password"
                required
                autoComplete="current-password"
                placeholder="Introduza a sua palavra-passe"
                className="mt-2 w-full rounded-[1rem] border border-ink/10 bg-white px-4 py-3 text-sm text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)] outline-none transition placeholder:text-ink/30 focus:border-ink/30 focus:ring-4 focus:ring-mist"
              />
            </label>

            <SubmitButton
              idleLabel="Entrar"
              pendingLabel="A validar acesso..."
              className="mt-2 w-full px-5 py-3 transition hover:bg-[#0e1932] focus:outline-none focus:ring-4 focus:ring-mist"
            />
          </form>

          <div className="mt-6 grid gap-3 border-t border-ink/10 pt-5 text-sm text-ink/65 sm:grid-cols-2">
            <p>O acesso é mantido por cookie de sessão e redirecionado automaticamente após autenticação.</p>
            <p>Se a sessão expirar, a plataforma devolve-o a esta página com a rota pretendida preservada.</p>
          </div>
        </section>
      </div>
    </main>
  );
}
