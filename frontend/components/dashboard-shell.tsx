import Link from "next/link";
import type { ReactNode } from "react";

type DashboardShellProps = {
  title: string;
  description: string;
  children: ReactNode;
};

const navigation = [
  { href: "/", label: "Visao Geral" },
  { href: "/gestao", label: "Gestao" },
  { href: "/curriculo", label: "Curriculo" },
  { href: "/avaliacao", label: "Avaliacao" },
];

export function DashboardShell({
  title,
  description,
  children,
}: DashboardShellProps) {
  return (
    <main className="relative overflow-hidden">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-grid bg-[size:34px_34px] opacity-40"
      />
      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8 sm:px-10 lg:px-12">
        <header className="mb-8 rounded-[2rem] border border-white/60 bg-white/80 p-8 shadow-card backdrop-blur">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="mb-3 inline-flex rounded-full border border-ink/10 bg-ember/10 px-4 py-1 text-sm font-semibold uppercase tracking-[0.25em] text-ember">
                Substrato Educacao
              </p>
              <h1 className="font-display text-4xl font-bold leading-tight text-ink sm:text-5xl">
                {title}
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-ink/75 sm:text-lg">
                {description}
              </p>
            </div>
            <nav className="flex flex-wrap gap-3">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-full border border-ink/10 bg-sand px-4 py-2 text-sm font-medium text-ink transition hover:border-ink/30 hover:bg-white"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>

        <div className="space-y-8">{children}</div>
      </div>
    </main>
  );
}
