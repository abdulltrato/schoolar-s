"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";

import { combineNavigationWithAside, computeShellSpacing, DashboardHeader } from "./dashboard-shell/header";
import type { HeaderNavLink } from "./dashboard-shell/header-nav";

type DashboardShellProps = {
  title: string;
  description: string;
  children: ReactNode;
  aside?: ReactNode;
  headerLinks?: HeaderNavLink[];
};

// Links padrão da navegação lateral.
const ASIDE_NAV_LINKS: HeaderNavLink[] = [
  { href: "/", label: "Visão geral" },
  { href: "/management", label: "Gestão" },
  { href: "/curriculum", label: "Currículo" },
  { href: "/assessment", label: "Avaliação" },
  { href: "/reports", label: "Relatórios" },
  { href: "/learning", label: "Ensino" },
  { href: "/student", label: "Portal do aluno" },
  { href: "/teacher", label: "Área do professor" },
  { href: "/finance", label: "Financeiro" },
  { href: "/communication", label: "Comunicação" },
  { href: "/crud", label: "CRUD" },
  { href: "/audit", label: "Auditoria" },
];

export function DashboardShell({ title, description, children, aside, headerLinks }: DashboardShellProps) {
  const pathname = usePathname();
  const headerRef = useRef<HTMLElement>(null);
  const footerRef = useRef<HTMLElement>(null);
  const [headerHeight, setHeaderHeight] = useState(0);
  const [footerHeight, setFooterHeight] = useState(0);

  // Observa header/footer para calcular espaçamento interno e altura de sticky.
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

    const resizeObserver = new ResizeObserver(syncLayout);

    resizeObserver.observe(header);
    resizeObserver.observe(footer);
    window.addEventListener("resize", syncLayout);

    return () => {
      resizeObserver.disconnect();
      window.removeEventListener("resize", syncLayout);
    };
  }, []);

  const { mainStyle, asideStyle } = computeShellSpacing({ headerHeight, footerHeight });
  const stickyTop = headerHeight ? headerHeight + 8 : 80;
  const stickyHeight = `calc(100vh - ${headerHeight + footerHeight + 40}px)`;

  return (
    <div className="min-h-screen overflow-hidden bg-[linear-gradient(180deg,#f3ecdd_0%,#f7f4ec_30%,#eef3f8_100%)] text-ink">
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-x-0 top-0 h-[32rem] bg-[radial-gradient(circle_at_top_left,rgba(217,108,6,0.2),transparent_24%),radial-gradient(circle_at_top_right,rgba(60,122,87,0.16),transparent_26%),linear-gradient(180deg,rgba(20,33,61,0.05),transparent)]"
      />
      <div aria-hidden="true" className="pointer-events-none fixed inset-0 bg-grid bg-[size:34px_34px] opacity-[0.16]" />
      <div aria-hidden="true" className="animate-drift-slow pointer-events-none fixed left-[-7rem] top-24 h-64 w-64 rounded-full bg-ember/12 blur-3xl" />
      <div aria-hidden="true" className="animate-drift-delayed pointer-events-none fixed bottom-12 right-[-6rem] h-72 w-72 rounded-full bg-fern/12 blur-3xl" />
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-ink focus:px-3 focus:py-2 focus:text-sm focus:text-sand"
      >
        Ir para o conteúdo
      </a>
      <div className="app-shell">
        <div className="grid lg:grid-cols-[15rem_1fr] gap-3">
          <aside className="hidden lg:block">
            <nav
              aria-label="Navegação lateral"
              className="sticky grid gap-1 overscroll-contain"
              style={{ top: `${stickyTop}px`, height: stickyHeight, overflowY: "auto" }}
            >
              {ASIDE_NAV_LINKS.map((link) => {
                const active = pathname === link.href;
                return (
                  <a
                    key={link.href}
                    href={link.href}
                    className={`rounded-[var(--radius-md)] border px-3 py-2 text-sm font-medium transition ${
                      active
                        ? "border-ink bg-ink text-sand shadow-sm"
                        : "border-ink/10 bg-white/90 text-ink hover:border-ink/25 hover:bg-white"
                    }`}
                  >
                    {link.label}
                  </a>
                );
              })}
            </nav>
          </aside>

          <div>
            <DashboardHeader
              title={title}
              description={description}
              headerRef={headerRef}
              footerRef={footerRef}
              headerLinks={headerLinks}
            />

            <main
              id="main-content"
              className="app-main-stack"
              style={{
                ...mainStyle,
                paddingTop: `calc(${mainStyle.paddingTop} + 8px)`,
              }}
            >
              <div style={{ height: stickyHeight, overflowY: "auto", overscrollBehavior: "contain" }}>
                {combineNavigationWithAside(children, aside, mainStyle, asideStyle)}
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
