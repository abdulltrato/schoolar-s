import Link from "next/link";
import { DashboardShell } from "@/components/dashboard-shell";
import { MetricCard } from "@/components/metric-card";
import { SectionTitle } from "@/components/section-title";
import { StatusCard } from "@/components/status-card";
import { getHomeSnapshot, type CollectionSnapshot } from "@/lib/api";

function toneForCollection(snapshot: CollectionSnapshot<unknown>) {
  return snapshot.ok ? "success" : "warning";
}

function statusForCollection(snapshot: CollectionSnapshot<unknown>) {
  if (snapshot.requiresAuth) {
    return "AUTH";
  }

  return snapshot.ok ? "ONLINE" : "OFFLINE";
}

export default async function Home() {
  const snapshot = await getHomeSnapshot();
  const modules = [
    {
      href: "/gestao",
      title: "Gestao",
      description: "Escolas, turmas, professores e cargos escolares.",
    },
    {
      href: "/curriculo",
      title: "Curriculo",
      description: "Oferta disciplinar e planos curriculares.",
    },
    {
      href: "/avaliacao",
      title: "Avaliacao",
      description: "Periodos, componentes, lancamentos e medias.",
    },
  ];

  return (
    <DashboardShell
      title="Painel executivo do ecossistema escolar"
      description="Visao geral da operacao escolar, estrutura curricular e avaliacao. Os detalhes agora vivem em modulos dedicados."
      aside={(
        <section className="rounded-[0.9rem] border border-ink/10 bg-ink p-2.5 text-sand shadow-card">
          <SectionTitle
            eyebrow="Modulos"
            title="Navegacao por dominio"
            description="A interface foi separada para reduzir ruido e permitir leitura por area funcional."
            inverse
          />
          <nav aria-label="Atalhos de modulos" className="mt-2 grid gap-2">
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
          value={String(snapshot.escolas.count)}
          detail="Unidades escolares registadas e ativas."
        />
        <MetricCard
          label="Gestao"
          value={String(snapshot.atribuicoesGestao.count)}
          detail="Cargos de coordenacao e direcao definidos."
        />
        <MetricCard
          label="Planos"
          value={String(snapshot.planosDisciplina.count)}
          detail="Planos curriculares por disciplina e classe."
        />
        <MetricCard
          label="Periodos"
          value={String(snapshot.periodos.count)}
          detail="Calendario avaliativo configurado."
        />
        <MetricCard
          label="Componentes"
          value={String(snapshot.componentes.count)}
          detail="ACS, ACP, testes, exames e trabalhos."
        />
        <MetricCard
          label="Resultados"
          value={String(snapshot.resultadosPeriodo.count)}
          detail="Medias ponderadas por disciplina."
        />
      </section>

      <section className="grid gap-2">
        <div className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-2.5 shadow-card backdrop-blur">
          <SectionTitle
            eyebrow="Estado"
            title="Conectividade da plataforma"
            description="Leitura resumida dos recursos principais. Use os modulos para detalhar cada dominio."
          />
          <div className="mt-2 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            <StatusCard
              title="Healthcheck"
              status={snapshot.health.status}
              tone={snapshot.health.ok ? "success" : "warning"}
              body={snapshot.health.message}
            />
            <StatusCard
              title="Readiness"
              status={snapshot.readiness.status}
              tone={snapshot.readiness.ok ? "success" : "warning"}
              body={snapshot.readiness.message}
            />
            <StatusCard
              title="Gestao API"
              status={statusForCollection(snapshot.atribuicoesGestao)}
              tone={toneForCollection(snapshot.atribuicoesGestao)}
              body={snapshot.atribuicoesGestao.message}
            />
            <StatusCard
              title="Curriculo API"
              status={statusForCollection(snapshot.planosDisciplina)}
              tone={toneForCollection(snapshot.planosDisciplina)}
              body={snapshot.planosDisciplina.message}
            />
            <StatusCard
              title="Avaliacao API"
              status={statusForCollection(snapshot.resultadosPeriodo)}
              tone={toneForCollection(snapshot.resultadosPeriodo)}
              body={snapshot.resultadosPeriodo.message}
            />
          </div>
        </div>
      </section>
    </DashboardShell>
  );
}
