import Link from "next/link";

import { getLocale, t } from "@/lib/locale";

export default async function SubstratoPage() {
  const locale = await getLocale();

  return (
    <main className="min-h-screen bg-white px-4 py-10 text-ink sm:px-8 lg:px-12">
      <div className="mx-auto max-w-4xl space-y-8">
        <header className="space-y-3">
          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-ink/60">{t(locale, "brand")}</p>
          <h1 className="font-display text-3xl font-bold tracking-tight">{t(locale, "substratoTitle")}</h1>
          <p className="text-sm text-ink/65">{t(locale, "substratoSubtitle")}</p>
        </header>

        <section className="rounded-2xl border border-ink/10 bg-white p-6 shadow-card sm:p-8">
          <h2 className="text-xl font-semibold text-ink">{t(locale, "mission")}</h2>
          <p className="mt-3 text-sm leading-6 text-ink/75">{t(locale, "missionText")}</p>
        </section>

        <section className="grid gap-4 rounded-2xl border border-ink/10 bg-white p-6 shadow-card sm:grid-cols-2 sm:p-8">
          <div>
            <h3 className="text-lg font-semibold text-ink">{t(locale, "whatWeDo")}</h3>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li>• {t(locale, "bulletSuite")}</li>
              <li>• {t(locale, "bulletIntegration")}</li>
              <li>• {t(locale, "bulletAudit")}</li>
              <li>• {t(locale, "bulletDash")}</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-ink">{t(locale, "howWeWork")}</h3>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li>• {t(locale, "bulletTenant")}</li>
              <li>• {t(locale, "bulletSecurity")}</li>
              <li>• {t(locale, "bulletObservability")}</li>
              <li>• {t(locale, "bulletUX")}</li>
            </ul>
          </div>
        </section>

        <section className="rounded-2xl border border-ink/10 bg-white p-6 shadow-card sm:p-8">
          <h3 className="text-lg font-semibold text-ink">{t(locale, "contact")}</h3>
          <p className="mt-3 text-sm text-ink/75">
            {t(locale, "contactText")}{" "}
            <a href="mailto:contato@substrato.org" className="font-semibold text-ink hover:text-ember">
              contato@substrato.org
            </a>{" "}
            {locale === "en" ? "or visit the main dashboard." : "ou visite o painel principal."}
          </p>
          <div className="mt-4">
            <Link
              href="/"
              className="inline-flex items-center rounded-full border border-ink/10 px-4 py-2 text-sm font-semibold text-ink hover:border-ink/30"
            >
              {t(locale, "backToPanel")}
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
