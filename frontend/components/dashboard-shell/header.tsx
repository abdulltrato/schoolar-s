"use client";

import type { CSSProperties, ReactNode, RefObject } from "react";
import Link from "next/link";

import { MetricBadges } from "./metric-badges";
import { HeaderNav, HeaderNavLink } from "./header-nav";

type DashboardHeaderProps = {
  title: string;
  description: string;
  headerRef: RefObject<HTMLElement | null>;
  footerRef: RefObject<HTMLElement | null>;
  heroBadges?: { label: string; value: string }[];
  headerLinks?: HeaderNavLink[];
};

type HeaderStyleProps = {
  headerHeight: number;
  footerHeight: number;
};

// Calcula espaçamentos do main/aside com base em alturas de header/footer.
export function computeShellSpacing({ headerHeight, footerHeight }: HeaderStyleProps): {
  mainStyle: CSSProperties;
  asideStyle: CSSProperties;
} {
  const mainStyle: CSSProperties = {
    paddingTop: headerHeight ? `${headerHeight + 8}px` : "5.5rem",
    paddingBottom: footerHeight ? `${footerHeight + 8}px` : "3.25rem",
  };

  const asideStyle: CSSProperties = {
    top: headerHeight ? `${headerHeight + 8}px` : "5.5rem",
  };

  return { mainStyle, asideStyle };
}

export function DashboardHeader({
  title,
  description,
  headerRef,
  footerRef,
  heroBadges,
  headerLinks,
}: DashboardHeaderProps) {
  // Cabeçalho do dashboard com badges e navegação secundária.
  return (
    <>
      <header
        ref={headerRef}
        className="app-header overflow-hidden rounded-none border border-white/65 bg-[linear-gradient(135deg,rgba(255,255,255,0.95),rgba(247,243,233,0.92))] p-2 shadow-card backdrop-blur sm:p-3"
      >
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-x-6 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(20,33,61,0.24),transparent)]"
        />
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <p className="inline-flex rounded-full border border-ember/20 bg-ember/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-ember">
              Substrato Educação
            </p>
            <p className="inline-flex rounded-full border border-ink/10 bg-white/70 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/55">
              Dashboard operacional
            </p>
          </div>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="min-w-0">
              <h1 className="font-display text-base font-semibold leading-tight sm:text-lg lg:text-[1.2rem]">
                {title}
              </h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-ink/72">
                {description}
              </p>
              <HeaderNav links={headerLinks || []} />
            </div>
            {heroBadges && heroBadges.length > 0 ? <MetricBadges items={heroBadges} /> : null}
          </div>
        </div>
      </header>
      <footer
        ref={footerRef}
        className="app-footer rounded-none border border-white/60 bg-[linear-gradient(135deg,rgba(255,255,255,0.92),rgba(247,243,233,0.9))] px-5 py-4 text-[11px] leading-5 text-ink/70 backdrop-blur"
      >
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <span className="font-semibold text-ink/80">Schoolar-S</span>
          <span className="text-ink/70">
            Sistema desenvolvido pela organização{" "}
            <Link href="/substrato" className="font-semibold text-ink hover:text-ember">
              Substrato
            </Link>
            .
          </span>
        </div>
        <div className="mt-1 text-ink/65">
          Copyright © {new Date().getFullYear()} Substrato. Todos os direitos reservados.
        </div>
      </footer>
    </>
  );
}

export function combineNavigationWithAside(
  mainContent: ReactNode,
  asideContent: ReactNode | undefined,
  mainStyle: CSSProperties,
  asideStyle: CSSProperties,
) {
  // Se não há aside, retorna apenas o conteúdo principal.
  if (!asideContent) {
    return (
      <section aria-label="Conteúdo da página" className="app-content-stack">
        {mainContent}
      </section>
    );
  }

  return (
    <div className="app-content-grid">
      <section aria-label="Conteúdo da página" className="app-content-stack">
        {mainContent}
      </section>
      <aside className="app-aside app-content-stack" style={asideStyle}>
        {asideContent}
      </aside>
    </div>
  );
}
