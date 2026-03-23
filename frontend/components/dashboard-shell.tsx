"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";

type DashboardShellProps = {
  title: string;
  description: string;
  children: ReactNode;
  aside?: ReactNode;
};

const navigation = [
  { href: "/", label: "Visão geral" },
  { href: "/management", label: "Gestão" },
  { href: "/curriculum", label: "Currículo" },
  { href: "/assessment", label: "Avaliação" },
  { href: "/reports", label: "Relatórios" },
  { href: "/learning", label: "Ensino" },
  { href: "/student", label: "Aluno" },
  { href: "/teacher", label: "Professor" },
  { href: "/finance", label: "Financeiro" },
  { href: "/communication", label: "Comunicação" },
  { href: "/audit", label: "Auditoria" },
];

export function DashboardShell({
  title,
  description,
  children,
  aside,
}: DashboardShellProps) {
  const headerRef = useRef<HTMLElement>(null);
  const footerRef = useRef<HTMLElement>(null);
  const [headerHeight, setHeaderHeight] = useState(0);
  const [footerHeight, setFooterHeight] = useState(0);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const header = headerRef.current;
    const footer = footerRef.current;

    if (!header || !footer) {
      return;
    }

    const syncLayout = () => {
      setHeaderHeight(header.offsetHeight);
      setFooterHeight(footer.offsetHeight);
    };

    syncLayout();

    const resizeObserver = new ResizeObserver(() => {
      syncLayout();
    });

    resizeObserver.observe(header);
    resizeObserver.observe(footer);
    window.addEventListener("resize", syncLayout);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener("resize", syncLayout);
    };
  }, []);

  useEffect(() => {
    const closeMenuOnDesktop = () => {
      if (window.innerWidth >= 1024) {
        setIsMenuOpen(false);
      }
    };

    closeMenuOnDesktop();
    window.addEventListener("resize", closeMenuOnDesktop);

    return () => {
      window.removeEventListener("resize", closeMenuOnDesktop);
    };
  }, []);

  const mainStyle: CSSProperties = {
    paddingTop: headerHeight ? `${headerHeight + 12}px` : "8rem",
    paddingBottom: footerHeight ? `${footerHeight + 12}px` : "4rem",
  };

  const asideStyle: CSSProperties = {
    top: headerHeight ? `${headerHeight + 12}px` : "8rem",
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(217,108,6,0.16),transparent_28%),radial-gradient(circle_at_top_right,rgba(60,122,87,0.12),transparent_24%),linear-gradient(180deg,#f7f3e9_0%,#fbf8f2_100%)] text-ink">
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 bg-grid bg-[size:34px_34px] opacity-30"
      />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-ink focus:px-3 focus:py-2 focus:text-sm focus:text-sand"
      >
        Ir para o conteúdo
      </a>
      <div className="app-shell">
        <header
          ref={headerRef}
          className="app-header rounded-[0.9rem] border border-ink/10 bg-white/95 p-2 shadow-card backdrop-blur sm:p-3"
        >
          <div className="flex items-start justify-between gap-2 lg:items-center">
            <div className="min-w-0 max-w-4xl flex-1">
              <p className="mb-1 inline-flex rounded-full border border-ember/20 bg-ember/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-ember">
                Substrato Educação
              </p>
              <h1 className="font-display text-lg font-bold leading-tight sm:text-xl lg:text-2xl">
                {title}
              </h1>
              <p className="mt-1 max-w-4xl text-xs leading-4 text-ink/75 sm:text-sm">
                {description}
              </p>
            </div>
            <button
              type="button"
              aria-expanded={isMenuOpen}
              aria-controls="menu-principal"
              aria-label={isMenuOpen ? "Fechar menu" : "Abrir menu"}
              onClick={() => setIsMenuOpen((value) => !value)}
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-ink/10 bg-sand text-ink lg:hidden"
            >
              <span className="relative block h-3.5 w-4">
                <span
                  className={`absolute left-0 top-0 h-[2px] w-4 rounded bg-current transition ${isMenuOpen ? "top-[6px] rotate-45" : ""}`}
                />
                <span
                  className={`absolute left-0 top-[6px] h-[2px] w-4 rounded bg-current transition ${isMenuOpen ? "opacity-0" : "opacity-100"}`}
                />
                <span
                  className={`absolute left-0 top-3 h-[2px] w-4 rounded bg-current transition ${isMenuOpen ? "top-[6px] -rotate-45" : ""}`}
                />
              </span>
            </button>
            <nav aria-label="Navegação principal" className="hidden flex-wrap gap-1.5 lg:flex">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-medium transition hover:border-ink/30 hover:bg-white sm:text-xs"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <nav
            id="menu-principal"
            aria-label="Navegação principal móvel"
            className={`${isMenuOpen ? "mt-2 grid" : "hidden"} gap-1.5 border-t border-ink/10 pt-2 lg:hidden`}
          >
            {navigation.map((item) => (
              <Link
                key={`mobile-${item.href}`}
                href={item.href}
                onClick={() => setIsMenuOpen(false)}
                className="rounded-[0.75rem] border border-ink/10 bg-sand px-3 py-2 text-xs font-medium text-ink transition hover:border-ink/30 hover:bg-white"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>

        <main id="main-content" className="app-main-stack" style={mainStyle}>
          {aside ? (
            <div className="app-content-grid">
              <section aria-label="Conteúdo da página" className="app-content-stack">
                {children}
              </section>
              <aside className="app-aside app-content-stack" style={asideStyle}>
                {aside}
              </aside>
            </div>
          ) : (
            <section aria-label="Conteúdo da página" className="app-content-stack">
              {children}
            </section>
          )}
        </main>

        <footer
          ref={footerRef}
          className="app-footer rounded-[0.8rem] border border-ink/10 bg-white/95 px-3 py-1.5 text-[11px] leading-4 text-ink/65 backdrop-blur"
        >
          Painel Schoolar-S. Navegação por domínio com interface otimizada para operações escolares.
        </footer>
      </div>
    </div>
  );
}
