"use client";

import Link from "next/link";

export type NavigationItem = {
  href: string;
  label: string;
  tooltip: string;
};

export const DASHBOARD_NAVIGATION: NavigationItem[] = [
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
  { href: "/crud", label: "CRUD", tooltip: "Operações completas de criação e manutenção" },
  { href: "/audit", label: "Auditoria", tooltip: "Trilha sensível de mudanças e geração de provas" },
];

type PrimaryNavigationProps = {
  items: NavigationItem[];
  pathname: string;
};

export function PrimaryNavigation({ items, pathname }: PrimaryNavigationProps) {
  return (
    <nav aria-label="Navegação principal" className="mt-4 hidden flex-wrap gap-2 lg:flex">
      {items.map((item) => {
        const isActive = pathname === item.href;

        return (
          <Link
            key={item.href}
            href={item.href}
            data-tooltip={item.tooltip}
            className={`rounded-[var(--radius-md)] border px-3 py-1.5 text-xs font-medium transition tooltip-target ${
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
  );
}

type MobileNavigationProps = {
  items: NavigationItem[];
  pathname: string;
  isOpen: boolean;
  onNavigate: () => void;
};

export function MobileNavigation({ items, pathname, isOpen, onNavigate }: MobileNavigationProps) {
  return (
    <nav
      id="menu-principal"
      aria-label="Navegação principal móvel"
      className={`${isOpen ? "mt-3 grid" : "hidden"} gap-2 border-t border-ink/10 pt-3 lg:hidden`}
    >
      {items.map((item) => {
        const isActive = pathname === item.href;

        return (
          <Link
            key={`mobile-${item.href}`}
            href={item.href}
            onClick={onNavigate}
            data-tooltip={item.tooltip}
            className={`rounded-[var(--radius-md)] border px-3 py-2.5 text-sm font-medium transition tooltip-target ${
              isActive ? "border-ink bg-ink text-sand" : "border-ink/10 bg-white/75 text-ink hover:border-ink/25 hover:bg-white"
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
