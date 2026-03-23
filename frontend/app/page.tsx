import Link from "next/link";
import { DashboardShell } from "@/components/dashboard-shell";
import { MetricCard } from "@/components/metric-card";
import { SectionTitle } from "@/components/section-title";
import { StatusCard } from "@/components/status-card";
import { getHomeSnapshot, requireAuthSession, type CollectionSnapshot } from "@/lib/api";

function toneForCollection(snapshot: CollectionSnapshot<unknown>) {
  return snapshot.ok ? "success" : "warning";
}

function statusForCollection(snapshot: CollectionSnapshot<unknown>) {
  if (snapshot.requiresAuth) {
    return "AUT";
  }

  return snapshot.ok ? "ONLINE" : "OFFLINE";
}

export default async function Home() {
  await requireAuthSession("/");
  const snapshot = await getHomeSnapshot();
  const modules = [
    {
      href: "/management",
      title: "Gestão",
      description: "Escolas, turmas, professores e cargos de liderança.",
    },
    {
      href: "/curriculum",
      title: "Currículo",
      description: "Oferta de disciplinas e planos curriculares.",
    },
    {
      href: "/assessment",
      title: "Avaliação",
      description: "Períodos, componentes, registos e resultados ponderados.",
    },
    {
      href: "/reports",
      title: "Relatórios",
      description: "Declarações, certificados, diplomas, pautas, estatísticas e listas operacionais.",
    },
    {
      href: "/learning",
      title: "Ensino",
      description: "Cursos, aulas, materiais, tarefas e submissões.",
    },
    {
      href: "/student",
      title: "Portal do aluno",
      description: "Registos do aluno: ensino, presença, resultados e faturas.",
    },
    {
      href: "/teacher",
      title: "Área do professor",
      description: "Alocações docentes, execução em turma e entrega académica.",
    },
    {
      href: "/finance",
      title: "Financeiro",
      description: "Faturas, pagamentos e acompanhamento financeiro do aluno.",
    },
    {
      href: "/communication",
      title: "Comunicação",
      description: "Comunicados e alcance de comunicação com as famílias.",
    },
    {
      href: "/audit",
      title: "Auditoria",
      description: "Trilha persistente de mudanças sensíveis em financeiro, comunicação, presença e avaliação.",
    },
  ];

  return (
    <DashboardShell
      title="Plataforma escolar executiva"
      description="Visão de alto nível das operações escolares, estrutura curricular e avaliação. Os detalhes estão organizados em módulos dedicados."
      aside={(
        <section className="rounded-[0.9rem] border border-ink/10 bg-ink p-2.5 text-sand shadow-card">
          <SectionTitle
            eyebrow="Módulos"
            title="Navegação por domínio"
            description="A interface está dividida por área funcional para reduzir ruído e melhorar a leitura operacional."
            inverse
          />
          <nav aria-label="Atalhos de módulos" className="mt-2 grid gap-2">
            {modules.map((module) => (
              <Link
                key={module.href}
                href={module.href}
                className="rounded-[0.8rem] border border-white/10 bg-white/5 px-2.5 py-2 transition hover:border-white/25 hover:bg-white/10"
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-sand sm:text-xs">
                  {module.title}
                </p>
                <p className="mt-1 text-xs leading-4 text-sand/78 sm:text-sm">
                  {module.description}
                </p>
              </Link>
            ))}
          </nav>
        </section>
      )}
    >
      <section className="grid gap-2 md:grid-cols-3 xl:grid-cols-6">
        <MetricCard
          label="Escolas"
          value={String(snapshot.schools.count)}
          detail="Unidades escolares registadas e ativas."
        />
        <MetricCard
          label="Gestão"
          value={String(snapshot.managementAssignments.count)}
          detail="Cargos de coordenação e liderança definidos."
        />
        <MetricCard
          label="Planos"
          value={String(snapshot.subjectPlans.count)}
          detail="Planos curriculares por disciplina e classe."
        />
        <MetricCard
          label="Períodos"
          value={String(snapshot.periods.count)}
          detail="Calendário avaliativo configurado."
        />
        <MetricCard
          label="Componentes"
          value={String(snapshot.components.count)}
          detail="ACS, ACP, testes, exames e trabalhos."
        />
        <MetricCard
          label="Resultados"
          value={String(snapshot.periodResults.count)}
          detail="Médias ponderadas por disciplina."
        />
      </section>

      <section className="grid gap-2">
        <div className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-2.5 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Estado"
            title="Conectividade da plataforma"
            description="Leitura rápida dos recursos centrais. Use os módulos para inspecionar cada domínio em detalhe."
          />
          <div className="mt-2 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            <StatusCard
              title="Saúde"
              status={snapshot.health.status}
              tone={snapshot.health.ok ? "success" : "warning"}
              body={snapshot.health.message}
            />
            <StatusCard
              title="Prontidão"
              status={snapshot.readiness.status}
              tone={snapshot.readiness.ok ? "success" : "warning"}
              body={snapshot.readiness.message}
            />
            <StatusCard
              title="API de gestão"
              status={statusForCollection(snapshot.managementAssignments)}
              tone={toneForCollection(snapshot.managementAssignments)}
              body={snapshot.managementAssignments.message}
            />
            <StatusCard
              title="API de currículo"
              status={statusForCollection(snapshot.subjectPlans)}
              tone={toneForCollection(snapshot.subjectPlans)}
              body={snapshot.subjectPlans.message}
            />
            <StatusCard
              title="API de avaliação"
              status={statusForCollection(snapshot.periodResults)}
              tone={toneForCollection(snapshot.periodResults)}
              body={snapshot.periodResults.message}
            />
          </div>
        </div>
      </section>
    </DashboardShell>
  );
}
