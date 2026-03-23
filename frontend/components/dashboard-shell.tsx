"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";

type DashboardShellProps = {
  title: string;
  description: string;
  children: ReactNode;
  aside?: ReactNode;
};

const navigation = [
  { href: "/", label: "Visão geral", tooltip: "Painel executivo com métricas e estado da plataforma" },
  { href: "/management", label: "Gestão", tooltip: "Escolas, turmas e cargos de liderança" },
  { href: "/curriculum", label: "Currículo", tooltip: "Oferta de disciplinas com planos curriculares" },
  { href: "/assessment", label: "Avaliação", tooltip: "Períodos, componentes e resultados finais" },
  { href: "/reports", label: "Relatórios", tooltip: "Geração e histórico de documentos oficiais" },
  { href: "/learning", label: "Ensino", tooltip: "Cursos, aulas, materiais e tarefas" },
  { href: "/student", label: "Aluno", tooltip: "Portal do aluno: presença, resultados e faturas" },
  { href: "/teacher", label: "Professor", tooltip: "Área do professor e alocações docentes" },
  { href: "/finance", label: "Financeiro", tooltip: "Faturas, pagamentos e acompanhamentos" },
  { href: "/communication", label: "Comunicação", tooltip: "Comunicados e alcance com as famílias" },
  { href: "/audit", label: "Auditoria", tooltip: "Trilha sensível de mudanças e geração de provas" },
];

export function DashboardShell({
  title,
  description,
  children,
  aside,
}: DashboardShellProps) {
  const pathname = usePathname();
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
    <div className="min-h-screen overflow-hidden bg-[linear-gradient(180deg,#f3ecdd_0%,#f7f4ec_30%,#eef3f8_100%)] text-ink">
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-x-0 top-0 h-[32rem] bg-[radial-gradient(circle_at_top_left,rgba(217,108,6,0.2),transparent_24%),radial-gradient(circle_at_top_right,rgba(60,122,87,0.16),transparent_26%),linear-gradient(180deg,rgba(20,33,61,0.05),transparent)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 bg-grid bg-[size:34px_34px] opacity-[0.16]"
      />
      <div aria-hidden="true" className="animate-drift-slow pointer-events-none fixed left-[-7rem] top-24 h-64 w-64 rounded-full bg-ember/12 blur-3xl" />
      <div aria-hidden="true" className="animate-drift-delayed pointer-events-none fixed bottom-12 right-[-6rem] h-72 w-72 rounded-full bg-fern/12 blur-3xl" />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-ink focus:px-3 focus:py-2 focus:text-sm focus:text-sand"
      >
        Ir para o conteúdo
      </a>
      <div className="app-shell">
        <header
          ref={headerRef}
          className="app-header overflow-hidden rounded-[1.5rem] border border-white/65 bg-[linear-gradient(135deg,rgba(255,255,255,0.95),rgba(247,243,233,0.92))] p-3 shadow-card backdrop-blur sm:p-4"
        >
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-x-6 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(20,33,61,0.24),transparent)]"
          />
          <div className="flex items-start justify-between gap-3 lg:items-start">
            <div className="min-w-0 max-w-4xl flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="inline-flex rounded-full border border-ember/20 bg-ember/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-ember">
                  Substrato Educação
                </p>
                <p className="inline-flex rounded-full border border-ink/10 bg-white/70 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/55">
                  Dashboard operacional
                </p>
              </div>
              <div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                <div className="min-w-0">
                  <h1 className="font-display text-xl font-bold leading-tight sm:text-2xl lg:text-[2rem]">
                    {title}
                  </h1>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-ink/72">
                    {description}
                  </p>
                </div>
                <div className="grid shrink-0 grid-cols-3 gap-2 text-center">
                  <div className="rounded-[1rem] border border-ink/10 bg-white/72 px-3 py-2.5">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink/45">Visão</p>
                    <p className="mt-1 font-display text-lg font-semibold text-ink">360</p>
                  </div>
                  <div className="rounded-[1rem] border border-ink/10 bg-white/72 px-3 py-2.5">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink/45">Domínios</p>
                    <p className="mt-1 font-display text-lg font-semibold text-ink">10</p>
                  </div>
                  <div className="rounded-[1rem] border border-ink/10 bg-white/72 px-3 py-2.5">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink/45">Modo</p>
                    <p className="mt-1 font-display text-lg font-semibold text-ink">Live</p>
                  </div>
                </div>
              </div>
            </div>
            <button
              type="button"
              aria-expanded={isMenuOpen}
              aria-controls="menu-principal"
              aria-label={isMenuOpen ? "Fechar menu" : "Abrir menu"}
              onClick={() => setIsMenuOpen((value) => !value)}
              className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-ink/10 bg-white/85 text-ink shadow-sm lg:hidden"
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
          </div>
          <nav aria-label="Navegação principal" className="mt-4 hidden flex-wrap gap-2 lg:flex">
            {navigation.map((item) => {
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  data-tooltip={item.tooltip}
                  className={`rounded-full border px-3 py-1.5 text-xs font-medium transition tooltip-target ${
                    isActive
                      ? "border-ink bg-ink text-sand shadow-[0_10px_30px_rgba(20,33,61,0.18)]"
                      : "border-ink/10 bg-white/78 text-ink hover:border-ink/25 hover:bg-white"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <nav
            id="menu-principal"
            aria-label="Navegação principal móvel"
            className={`${isMenuOpen ? "mt-3 grid" : "hidden"} gap-2 border-t border-ink/10 pt-3 lg:hidden`}
          >
            {navigation.map((item) => {
              const isActive = pathname === item.href;

              return (
                <Link
                  key={`mobile-${item.href}`}
                  href={item.href}
                  onClick={() => setIsMenuOpen(false)}
                  data-tooltip={item.tooltip}
                  className={`rounded-[1rem] border px-3 py-2.5 text-sm font-medium transition tooltip-target ${
                    isActive
                      ? "border-ink bg-ink text-sand"
                      : "border-ink/10 bg-white/75 text-ink hover:border-ink/25 hover:bg-white"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
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
          className="app-footer rounded-[1rem] border border-white/60 bg-[linear-gradient(135deg,rgba(255,255,255,0.92),rgba(247,243,233,0.9))] px-3 py-2 text-[11px] leading-4 text-ink/65 backdrop-blur"
        >
          Painel Schoolar-S. Navegação por domínio com interface otimizada para operações escolares.
        </footer>
      </div>
    </div>
  );
}
