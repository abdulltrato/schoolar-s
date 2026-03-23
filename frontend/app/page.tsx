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
        <section className="overflow-hidden rounded-[1.5rem] border border-white/15 bg-[linear-gradient(180deg,#13203c_0%,#1b2d52_100%)] p-4 text-sand shadow-card">
          <div aria-hidden className="mb-4 h-px bg-[linear-gradient(90deg,transparent,rgba(247,243,233,0.4),transparent)]" />
          <SectionTitle
            eyebrow="Módulos"
            title="Navegação por domínio"
            description="A interface está dividida por área funcional para reduzir ruído e melhorar a leitura operacional."
            inverse
          />
          <div className="mt-5 rounded-[1.1rem] border border-white/10 bg-white/5 px-4 py-3">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/55">Direção</p>
            <p className="mt-2 text-sm leading-6 text-sand/76">
              Atalhos para áreas críticas com descrição curta e leitura rápida para operação diária.
            </p>
          </div>
          <nav aria-label="Atalhos de módulos" className="mt-4 grid gap-2">
            {modules.map((module) => (
              <Link
                key={module.href}
                href={module.href}
                className="rounded-[1rem] border border-white/10 bg-white/5 px-3 py-3 transition hover:border-white/25 hover:bg-white/10"
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-sand sm:text-xs">
                  {module.title}
                </p>
                <p className="mt-1.5 text-sm leading-5 text-sand/78">
                  {module.description}
                </p>
              </Link>
            ))}
          </nav>
        </section>
      )}
    >
      <section className="overflow-hidden rounded-[1.6rem] border border-white/70 bg-[linear-gradient(135deg,rgba(20,33,61,0.98),rgba(32,52,85,0.94))] p-5 text-sand shadow-card">
        <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-ember">Centro de controlo</p>
            <h2 className="mt-3 max-w-2xl font-display text-3xl font-bold leading-tight sm:text-4xl">
              Uma leitura operacional clara do ecossistema escolar.
            </h2>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-sand/74">
              A home agora funciona como cockpit executivo: estado da plataforma, densidade certa de informação e acesso imediato aos módulos com maior impacto.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
            <div className="rounded-[1.1rem] border border-white/10 bg-white/7 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/55">Panorama</p>
              <p className="mt-2 font-display text-2xl font-semibold text-white">Live</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/10 bg-white/7 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/55">Cobertura</p>
              <p className="mt-2 font-display text-2xl font-semibold text-white">{modules.length}</p>
            </div>
            <div className="rounded-[1.1rem] border border-white/10 bg-white/7 px-4 py-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sand/55">Sessão</p>
              <p className="mt-2 font-display text-2xl font-semibold text-white">Ativa</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
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
        <div className="rounded-[1.5rem] border border-white/70 bg-white/88 p-4 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Estado"
            title="Conectividade da plataforma"
            description="Leitura rápida dos recursos centrais. Use os módulos para inspecionar cada domínio em detalhe."
          />
          <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
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
