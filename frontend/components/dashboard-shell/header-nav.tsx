"use client";

import Link from "next/link";

export type HeaderNavLink = {
  href: string;
  label: string;
  tooltip?: string;
};

type HeaderNavProps = {
  links: HeaderNavLink[];
};

export function HeaderNav({ links }: HeaderNavProps) {
  // Oculta quando não há links de atalho.
  if (!links || links.length === 0) return null;

  return (
    <nav aria-label="Atalhos do cabeçalho" className="mt-2 flex flex-wrap gap-1.5">
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          data-tooltip={link.tooltip}
          className="tooltip-target rounded-[var(--radius-sm)] border border-ink/15 bg-white/85 px-2.5 py-1 text-[11px] font-medium text-ink/80 hover:border-ink/30 hover:text-ink transition"
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
