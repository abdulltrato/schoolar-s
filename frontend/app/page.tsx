import { MetricCard } from "@/components/metric-card";
import { SectionTitle } from "@/components/section-title";
import { StatusCard } from "@/components/status-card";
import { getPlatformSnapshot } from "@/lib/api";

const highlights = [
  {
    label: "Arquitetura",
    value: "Frontend App Router",
    detail: "Next.js com TypeScript, Tailwind e runtime preparado para API separada.",
  },
  {
    label: "Operacao",
    value: "Docker + Kubernetes",
    detail: "Build standalone e manifests basicos para deploy do painel.",
  },
  {
    label: "Direcao",
    value: "Educacao orientada a competencias",
    detail: "Interface inicial focada em status da plataforma e dominios do backend.",
  },
];

const modules = [
  "Academico",
  "Curriculo",
  "Avaliacao",
  "Progresso",
  "Escola",
  "Relatorios",
  "Eventos",
];

export default async function Home() {
  const snapshot = await getPlatformSnapshot();

  return (
    <main className="relative overflow-hidden">
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-grid bg-[size:34px_34px] opacity-40"
      />
      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8 sm:px-10 lg:px-12">
        <header className="mb-10 rounded-[2rem] border border-white/60 bg-white/80 p-8 shadow-card backdrop-blur">
          <div className="mb-8 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="mb-3 inline-flex rounded-full border border-ink/10 bg-ember/10 px-4 py-1 text-sm font-semibold uppercase tracking-[0.25em] text-ember">
                Substrato Educacao
              </p>
              <h1 className="font-display text-4xl font-bold leading-tight text-ink sm:text-5xl lg:text-6xl">
                Painel de plataforma para ensino basico em escala.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-ink/75 sm:text-lg">
                Uma base inicial para operacao nacional: status tecnico, dominios
                do backend e stack pronta para entrega moderna em containers.
              </p>
            </div>
            <div className="rounded-[1.5rem] bg-ink px-6 py-5 text-sand shadow-card">
              <p className="text-xs uppercase tracking-[0.3em] text-sand/70">
                Backend alvo
              </p>
              <p className="mt-2 font-display text-2xl font-semibold">
                {snapshot.baseUrlLabel}
              </p>
              <p className="mt-2 max-w-xs text-sm leading-6 text-sand/75">
                Ajuste via <code>NEXT_PUBLIC_API_BASE_URL</code> e{" "}
                <code>API_BASE_URL</code>.
              </p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {highlights.map((item) => (
              <MetricCard
                key={item.label}
                label={item.label}
                value={item.value}
                detail={item.detail}
              />
            ))}
          </div>
        </header>

        <section className="mb-10 grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="rounded-[2rem] border border-ink/10 bg-white/80 p-8 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Conectividade"
              title="Saude operacional do backend"
              description="Leitura em tempo real dos endpoints de plataforma expostos pelo Django."
            />
            <div className="mt-6 grid gap-4 md:grid-cols-2">
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
            </div>
          </div>

          <div className="rounded-[2rem] border border-ink/10 bg-ink p-8 text-sand shadow-card">
            <SectionTitle
              eyebrow="Infra"
              title="Pronto para empacotamento"
              description="O frontend nasce com build standalone e manifests para deploy em cluster."
              inverse
            />
            <div className="mt-6 space-y-3 text-sm leading-6 text-sand/78">
              <p>Imagem baseada em Node 22 Alpine com multi-stage build.</p>
              <p>Service interno na porta 3000 e probes HTTP em Kubernetes.</p>
              <p>ConfigMap para URL do backend sem rebuild da imagem em producao.</p>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-[2rem] border border-ink/10 bg-white/75 p-8 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Dominios"
              title="Modulos atuais do backend"
              description="Mapa inicial dos bounded contexts ja expostos pela API."
            />
            <div className="mt-6 flex flex-wrap gap-3">
              {modules.map((module) => (
                <span
                  key={module}
                  className="rounded-full border border-ink/10 bg-mist px-4 py-2 text-sm font-medium text-ink"
                >
                  {module}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] border border-ink/10 bg-gradient-to-br from-ember/10 via-white/70 to-fern/10 p-8 shadow-card">
            <SectionTitle
              eyebrow="Proximos blocos"
              title="Base pronta para evolucao funcional"
              description="A proxima camada natural e transformar este painel em uma aplicacao de produto."
            />
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <MetricCard
                label="Autenticacao"
                value="Login e RBAC"
                detail="Conectar perfis de professor, diretor, admin e governo."
              />
              <MetricCard
                label="Operacao"
                value="Dashboards por tenant"
                detail="Indicadores de aprovacao, retencao e evolucao por competencia."
              />
              <MetricCard
                label="Fluxo"
                value="CRUD por dominio"
                detail="Consumir `/api/v1/*` com formularios e listagens tipadas."
              />
              <MetricCard
                label="Entrega"
                value="Pipeline CI/CD"
                detail="Automatizar build, scan e rollout para ambientes distintos."
              />
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
