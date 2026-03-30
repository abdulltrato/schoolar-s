import Link from "next/link";

import { changePasswordAction, updateProfileAction } from "@/app/profile/actions";
import { AvatarInput } from "@/components/avatar-input";
import { requireAuthSession } from "@/lib/api";
import { getLocale, t } from "@/lib/locale";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

// Lê query param simples.
function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

export default async function ProfilePage({ searchParams }: PageProps) {
  // Garante sessão válida antes de exibir formulário.
  const user = await requireAuthSession("/profile");
  const locale = await getLocale();
  const params = (await searchParams) || {};
  const status = readParam(params.status);
  const detail = readParam(params.detail);

  return (
    <main className="min-h-screen bg-white px-4 py-10 text-ink sm:px-8 lg:px-12">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-ink/60">Conta</p>
            <h1 className="font-display text-3xl font-bold tracking-tight">{t(locale, "profileTitle")}</h1>
            <p className="text-sm text-ink/65">{t(locale, "profileSubtitle")}</p>
          </div>
          <Link href="/" className="rounded-full border border-ink/10 px-4 py-2 text-sm font-semibold text-ink">
            {t(locale, "backToDashboard")}
          </Link>
        </div>

        {status === "perfil_atualizado" && (
          <div className="rounded-xl border border-fern/30 bg-fern/10 px-4 py-3 text-sm text-fern">Perfil atualizado.</div>
        )}
        {status === "perfil_erro" && (
          <div className="rounded-xl border border-ember/30 bg-ember/10 px-4 py-3 text-sm text-ember">Não foi possível atualizar o perfil.</div>
        )}
        {status === "senha_atualizada" && (
          <div className="rounded-xl border border-fern/30 bg-fern/10 px-4 py-3 text-sm text-fern">Palavra-passe alterada.</div>
        )}
        {status === "senha_erro" && (
          <div className="rounded-xl border border-ember/30 bg-ember/10 px-4 py-3 text-sm text-ember">
            {detail ? decodeURIComponent(detail) : "Não foi possível alterar a palavra-passe. Verifique a atual e a nova política."}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="rounded-2xl border border-ink/10 bg-white p-6 shadow-card sm:p-8">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-ink/60">
                  {t(locale, "identity")}
                </p>
                <h2 className="font-display text-2xl font-bold tracking-tight">{t(locale, "dataPhoto")}</h2>
              </div>
              <span className="rounded-full bg-mist px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                {user.role || "sem função"}
              </span>
            </div>

            <form action={updateProfileAction} className="mt-6 grid gap-5">
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-2">
                  <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                    {t(locale, "firstName")}
                  </span>
                  <input
                    name="first_name"
                    defaultValue={user.first_name}
                    placeholder="Primeiro nome"
                    className="rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-ink/40 focus:ring-4 focus:ring-mist"
                  />
                </label>
                <label className="grid gap-2">
                  <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                    {t(locale, "lastName")}
                  </span>
                  <input
                    name="last_name"
                    defaultValue={user.last_name}
                    placeholder="Último nome"
                    className="rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-ink/40 focus:ring-4 focus:ring-mist"
                  />
                </label>
              </div>

              <AvatarInput initialUrl={user.avatar_url || ""} />

              <button
                type="submit"
                className="w-full rounded-xl bg-ink px-4 py-3 text-sm font-semibold text-sand transition hover:bg-[#0f1a31] focus:outline-none focus:ring-4 focus:ring-mist"
              >
                {t(locale, "saveProfile")}
              </button>
            </form>
          </section>

          <section className="rounded-2xl border border-ink/10 bg-white p-6 shadow-card sm:p-8">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-ink/60">{t(locale, "security")}</p>
            <h2 className="font-display text-2xl font-bold tracking-tight">{t(locale, "changePassword")}</h2>
            <p className="mt-2 text-sm text-ink/65">A sessão permanece ativa após a troca.</p>

            <form action={changePasswordAction} className="mt-6 grid gap-4">
              <label className="grid gap-2">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                  {t(locale, "passwordCurrent")}
                </span>
                <input
                  name="old_password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-ink/40 focus:ring-4 focus:ring-mist"
                />
              </label>
              <label className="grid gap-2">
                <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink/70">
                  {t(locale, "passwordNew")}
                </span>
                <input
                  name="new_password"
                  type="password"
                  autoComplete="new-password"
                  required
                  className="rounded-xl border border-ink/15 bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-ink/40 focus:ring-4 focus:ring-mist"
                />
              </label>

              <button
                type="submit"
                className="w-full rounded-xl bg-ink px-4 py-3 text-sm font-semibold text-sand transition hover:bg-[#0f1a31] focus:outline-none focus:ring-4 focus:ring-mist"
              >
                {t(locale, "changePassword")}
              </button>
            </form>
          </section>
        </div>
      </div>
    </main>
  );
}
