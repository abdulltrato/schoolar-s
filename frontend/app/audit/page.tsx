import { revalidatePath } from "next/cache";
import { DashboardShell } from "@/components/dashboard-shell";
import { MetricCard } from "@/components/metric-card";
import { RecordList } from "@/components/record-list";
import { SectionTitle } from "@/components/section-title";
import { StatusCard } from "@/components/status-card";
import { SubmitButton } from "@/components/submit-button";
import { formatAuditAction, formatAuditSeverity } from "@/lib/labels";
import {
  acknowledgeAuditAlert,
  getAuditSnapshot,
  handleMutationRedirectTo,
  requireAuthSession,
  type AuditAlert,
  type AuditEvent,
} from "@/lib/api";

type RankedEntry = {
  label: string;
  count: number;
};

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] || "" : value || "";
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-PT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function topCounts(values: string[], limit = 3) {
  const counts = new Map<string, number>();
  for (const value of values.filter(Boolean)) {
    counts.set(value, (counts.get(value) || 0) + 1);
  }
  return Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit);
}

function riskTone(flagged: boolean): "success" | "warning" {
  return flagged ? "warning" : "success";
}

function buildAuditHref(params: Record<string, string>) {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value));
  return `/audit${query.toString() ? `?${query.toString()}` : ""}`;
}

async function acknowledgeAuditAlertAction(formData: FormData) {
  "use server";

  const id = Number(formData.get("id"));
  const pageHref = String(formData.get("page_href") || "/audit");
  const result = await acknowledgeAuditAlert(id);

  revalidatePath("/audit");
  await handleMutationRedirectTo(result, pageHref, "alert-acknowledged", "alert-acknowledge-error");
}

export default async function AuditPage({ searchParams }: PageProps) {
  const params = (await searchParams) || {};
  const resource = readParam(params.resource);
  const action = readParam(params.action);
  const severity = readParam(params.severity);
  const acknowledged = readParam(params.acknowledged);
  const username = readParam(params.username);
  const tenantId = readParam(params.tenant_id);
  const dateFrom = readParam(params.date_from);
  const dateTo = readParam(params.date_to);
  const status = readParam(params.status);
  const page = Math.max(Number(readParam(params.page) || "1") || 1, 1);

  const currentHref = buildAuditHref({
    resource,
    action,
    severity,
    acknowledged,
    username,
    tenant_id: tenantId,
    date_from: dateFrom,
    date_to: dateTo,
    page: String(page),
  });

  await requireAuthSession(currentHref);
  const snapshot = await getAuditSnapshot({
    page,
    resource,
    action,
    severity,
    acknowledged,
    username,
    tenant_id: tenantId,
    date_from: dateFrom,
    date_to: dateTo,
  });

  const queryWithoutPage = new URLSearchParams(
    Object.entries({
      resource,
      action,
      severity,
      acknowledged,
      username,
      tenant_id: tenantId,
      date_from: dateFrom,
      date_to: dateTo,
    }).filter(([, value]) => value),
  );

  const previousHref =
    page > 1 ? `/audit?${new URLSearchParams([...queryWithoutPage.entries(), ["page", String(page - 1)]]).toString()}` : null;
  const nextHref =
    snapshot.auditEvents.next
      ? `/audit?${new URLSearchParams([...queryWithoutPage.entries(), ["page", String(page + 1)]]).toString()}`
      : null;
  const exportBaseQuery = queryWithoutPage.toString();
  const csvExportHref = `/api/v1/school/audit-events/exports/download/${exportBaseQuery ? `?${exportBaseQuery}&export_format=csv` : "?export_format=csv"}`;
  const jsonExportHref = `/api/v1/school/audit-events/exports/download/${exportBaseQuery ? `?${exportBaseQuery}&export_format=json` : "?export_format=json"}`;
  const auditItems = snapshot.auditEvents.items;
  const alertItems = snapshot.auditAlerts.items;
  const recent24hCount = auditItems.filter((event) => Date.now() - new Date(event.created_at).getTime() <= 24 * 60 * 60 * 1000).length;
  const uniqueActors = new Set(auditItems.map((event) => event.username).filter(Boolean)).size;
  const uniqueTenants = new Set(auditItems.map((event) => event.tenant_id).filter(Boolean)).size;
  const topResources: RankedEntry[] = topCounts(auditItems.map((event) => event.resource)).map(([label, count]) => ({ label, count }));
  const topActors: RankedEntry[] = topCounts(auditItems.map((event) => event.username)).map(([label, count]) => ({ label, count }));
  const latestEvent = auditItems[0];
  const latestAlert = alertItems[0];
  const rankedSnapshot = {
    ...snapshot.auditEvents,
    items: [] as RankedEntry[],
  };
  const actorDominanceRatio = snapshot.auditEvents.count > 0 && topActors[0] ? topActors[0].count / snapshot.auditEvents.count : 0;
  const resourceDominanceRatio = snapshot.auditEvents.count > 0 && topResources[0] ? topResources[0].count / snapshot.auditEvents.count : 0;
  const highRecentVolume = recent24hCount >= 10;
  const highActorConcentration = actorDominanceRatio >= 0.5;
  const highResourceConcentration = resourceDominanceRatio >= 0.6;
  const suspiciousSignals = [
    highRecentVolume ? `Volume recente elevado: ${recent24hCount} eventos nas últimas 24h.` : null,
    highActorConcentration && topActors[0] ? `Concentração por ator: ${topActors[0].label} representa ${Math.round(actorDominanceRatio * 100)}% dos eventos visíveis.` : null,
    highResourceConcentration && topResources[0] ? `Concentração por recurso: ${topResources[0].label} representa ${Math.round(resourceDominanceRatio * 100)}% dos eventos visíveis.` : null,
  ].filter(Boolean) as string[];
  const riskLevel = suspiciousSignals.length >= 2 ? "ELEVATED" : suspiciousSignals.length === 1 ? "WATCH" : "STABLE";
  const riskToneValue = suspiciousSignals.length > 0;
  const openAlertCount = alertItems.filter((alert) => !alert.acknowledged).length;
  const elevatedAlertCount = alertItems.filter((alert) => alert.severity === "elevated").length;

  return (
    <DashboardShell
      title="Trilha de auditoria"
      description="Rastreio operacional de mudanças sensíveis em recursos, atores, tenants e rotas."
      aside={(
        <>
          <section className="rounded-[1.25rem] border border-ink/10 bg-white/80 p-4 shadow-card backdrop-blur">
            <SectionTitle
              eyebrow="Auditoria"
              title="Superfície de controlo"
              description="Investigue operações sensíveis sem recorrer ao Django admin."
            />
            <dl className="mt-4 space-y-3 text-sm leading-5 text-ink/72">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Eventos</dt>
                <dd>{snapshot.auditEvents.count} registos de auditoria persistidos.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Recursos</dt>
                <dd>{new Set(snapshot.auditEvents.items.map((event) => event.resource)).size} tipos de recurso auditados.</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Atores</dt>
                <dd>{new Set(snapshot.auditEvents.items.map((event) => event.username).filter(Boolean)).size} utilizadores com mutações visíveis.</dd>
              </div>
            </dl>
          </section>
          <nav aria-label="Navegação secundária da auditoria" className="rounded-[1.25rem] border border-ink/10 bg-sand p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/55">Secções</p>
            <ul className="mt-3 space-y-2 text-sm text-ink/75">
              <li><a href="#audit-events">Eventos de auditoria</a></li>
            </ul>
          </nav>
        </>
      )}
    >
      {status ? (
        <section className={`rounded-[0.9rem] border px-3 py-2 text-sm ${status.endsWith("error") ? "border-ember/20 bg-ember/10 text-ember" : "border-fern/20 bg-fern/10 text-fern"}`}>
          {status === "alert-acknowledged" && "Alerta reconhecido com sucesso."}
          {status === "alert-acknowledge-error" && "Não foi possível reconhecer o alerta."}
          {status === "session_expired" && "A sua sessão expirou. Entre novamente para continuar."}
        </section>
      ) : null}

      <section className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Eventos visíveis"
          value={String(snapshot.auditEvents.count)}
          detail="Volume paginado devolvido pelo backend após filtros aplicados no servidor."
        />
        <MetricCard
          label="Últimas 24h"
          value={String(recent24hCount)}
          detail="Pressão recente de auditoria em operações sensíveis."
        />
        <MetricCard
          label="Atores"
          value={String(uniqueActors)}
          detail="Utilizadores distintos no recorte atual."
        />
        <MetricCard
          label="Tenants"
          value={String(uniqueTenants)}
          detail="Distribuição de tenants coberta pelos filtros aplicados."
        />
        <MetricCard
          label="Alertas abertos"
          value={String(openAlertCount)}
          detail="Alertas persistidos ainda não reconhecidos."
        />
      </section>

      <section className="grid gap-2 lg:grid-cols-4">
        <StatusCard
          title="Nível de risco"
          status={riskLevel}
          tone={riskTone(riskToneValue)}
          body={
            suspiciousSignals.length > 0
              ? suspiciousSignals.join(" ")
              : "Nenhum limiar de anomalia simples foi ultrapassado no recorte atual."
          }
        />
        <StatusCard
          title="Última mutação"
          status={latestEvent ? latestEvent.action.toUpperCase() : "VAZIO"}
          tone={latestEvent ? "warning" : "success"}
          body={
            latestEvent
              ? `${latestEvent.resource} por ${latestEvent.username || "utilizador desconhecido"} às ${formatDateTime(latestEvent.created_at)}.`
              : "Nenhum evento de auditoria está visível com os filtros atuais."
          }
        />
        <StatusCard
          title="Recurso dominante"
          status={topResources[0]?.label?.toUpperCase() || "VAZIO"}
          tone={topResources.length > 0 ? "warning" : "success"}
          body={
            topResources.length > 0
              ? `${topResources[0].count} eventos no recorte atual.`
              : "Não existe recurso dominante no conjunto de filtros."
          }
        />
        <StatusCard
          title="Ator dominante"
          status={topActors[0]?.label || "VAZIO"}
          tone={topActors.length > 0 ? "warning" : "success"}
          body={
            topActors.length > 0
              ? `${topActors[0].count} mutações atribuídas a este utilizador.`
              : "Sem concentração de atores no recorte atual."
          }
        />
        <StatusCard
          title="Último alerta"
          status={latestAlert ? latestAlert.severity.toUpperCase() : "SEM ALERTAS"}
          tone={latestAlert ? "warning" : "success"}
          body={
            latestAlert
              ? `${latestAlert.alert_type} | ${latestAlert.summary}`
              : "Nenhum alerta persistido foi disparado."
          }
        />
      </section>

      <form className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-2.5 shadow-card backdrop-blur">
        <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Recurso</span>
            <select name="resource" defaultValue={resource} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm">
              <option value="">Todos</option>
              {Array.from(new Set([...snapshot.auditEvents.items.map((event) => event.resource), ...snapshot.auditAlerts.items.map((alert) => alert.resource)].filter(Boolean))).map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Ação</span>
            <select name="action" defaultValue={action} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm">
              <option value="">Todos</option>
              {Array.from(new Set(snapshot.auditEvents.items.map((event) => event.action))).map((item) => (
                <option key={item} value={item}>{formatAuditAction(item)}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Severidade</span>
            <select name="severity" defaultValue={severity} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm">
              <option value="">Todas</option>
              <option value="watch">{formatAuditSeverity("watch")}</option>
              <option value="elevated">{formatAuditSeverity("elevated")}</option>
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Estado do alerta</span>
            <select name="acknowledged" defaultValue={acknowledged} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm">
              <option value="">Todos</option>
              <option value="false">Aberto</option>
              <option value="true">Reconhecido</option>
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Utilizador</span>
            <select name="username" defaultValue={username} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm">
              <option value="">Todos</option>
              {Array.from(new Set([...snapshot.auditEvents.items.map((event) => event.username), ...snapshot.auditAlerts.items.map((alert) => alert.username)].filter(Boolean))).map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Tenant</span>
            <select name="tenant_id" defaultValue={tenantId} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm">
              <option value="">Todos</option>
              {Array.from(new Set([...snapshot.auditEvents.items.map((event) => event.tenant_id), ...snapshot.auditAlerts.items.map((alert) => alert.tenant_id)].filter(Boolean))).map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Data de início</span>
            <input name="date_from" type="date" defaultValue={dateFrom} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm" />
          </label>
          <label className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Data de fim</span>
            <input name="date_to" type="date" defaultValue={dateTo} className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink sm:text-sm" />
          </label>
        </div>
        <div className="mt-2 flex gap-1.5">
          <button type="submit" className="rounded-full bg-ink px-2.5 py-1 text-[11px] font-semibold text-sand sm:text-xs">
            Filtrar
          </button>
          <a href="/audit" className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink sm:text-xs">
            Limpar
          </a>
          <a href={csvExportHref} className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink sm:text-xs">
            Exportar CSV
          </a>
          <a href={jsonExportHref} className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink sm:text-xs">
            Exportar JSON
          </a>
        </div>
      </form>

      <section id="audit-events" className="grid gap-4">
        <RecordList
          title="Alertas de auditoria"
          subtitle="Alertas gerados automaticamente por limiares no último ciclo."
          snapshot={snapshot.auditAlerts}
          rows={snapshot.auditAlerts.items.slice(0, 8)}
          renderRow={(alert: AuditAlert) => (
            <div key={alert.id} className={`rounded-[0.95rem] border px-3 py-3 ${alert.severity === "elevated" ? "border-ember/20 bg-ember/5" : "border-ink/10 bg-white"}`}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{alert.alert_type}</p>
                <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] ${alert.severity === "elevated" ? "bg-ember/10 text-ember" : "bg-sand text-ink/75"}`}>
                  {formatAuditSeverity(alert.severity)}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">{alert.summary}</p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {alert.username || "system"} {alert.resource ? `| ${alert.resource}` : ""} {alert.tenant_id ? `| ${alert.tenant_id}` : ""}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {formatDateTime(alert.created_at)} | {alert.acknowledged ? "reconhecido" : "aberto"} | alertas elevados visíveis: {elevatedAlertCount}
              </p>
              {!alert.acknowledged ? (
                <form action={acknowledgeAuditAlertAction} className="mt-2">
                  <input type="hidden" name="id" value={alert.id} />
                  <input type="hidden" name="page_href" value={currentHref} />
                  <SubmitButton idleLabel="Reconhecer alerta" pendingLabel="A reconhecer..." />
                </form>
              ) : null}
            </div>
          )}
        />

        <section className="grid gap-4 lg:grid-cols-2">
          <RecordList
            title="Principais recursos"
            subtitle="Recursos com maior número de mutações no recorte atual."
            snapshot={rankedSnapshot}
            rows={topResources}
            renderRow={(entry: RankedEntry) => (
              <div key={entry.label} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <p className="font-semibold text-ink">{entry.label}</p>
                <p className="mt-1 text-sm leading-5 text-ink/55">{entry.count} eventos</p>
              </div>
            )}
          />
          <RecordList
            title="Principais atores"
            subtitle="Utilizadores com maior volume de mutações no recorte atual."
            snapshot={rankedSnapshot}
            rows={topActors}
            renderRow={(entry: RankedEntry) => (
              <div key={entry.label} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
                <p className="font-semibold text-ink">{entry.label}</p>
                <p className="mt-1 text-sm leading-5 text-ink/55">{entry.count} eventos</p>
              </div>
            )}
          />
        </section>

        <RecordList
          title="Eventos de auditoria"
          subtitle="Operações sensíveis (criação/atualização) persistidas pelo backend."
          snapshot={snapshot.auditEvents}
          rows={snapshot.auditEvents.items}
          renderRow={(event: AuditEvent) => (
            <div key={event.id} className="rounded-[0.95rem] border border-ink/10 bg-white px-3 py-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">
                  {event.resource} #{event.object_id}
                </p>
                <span className="rounded-full bg-mist px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-ink/70">
                  {formatAuditAction(event.action)}
                </span>
              </div>
              <p className="mt-1.5 text-sm leading-5 text-ink/70">
                {event.username || "utilizador desconhecido"} {event.role ? `| ${event.role}` : ""} {event.tenant_id ? `| ${event.tenant_id}` : ""}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {event.method} {event.path}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {formatDateTime(event.created_at)} | alterações: {event.changed_fields.length > 0 ? event.changed_fields.join(", ") : "nenhum campo capturado"}
              </p>
              <p className="mt-1 text-sm leading-5 text-ink/55">
                {event.object_repr || "Sem etiqueta do objeto"} | pedido {event.request_id || "-"}
              </p>
            </div>
          )}
        />
        <div className="flex items-center justify-between rounded-[0.9rem] border border-ink/10 bg-white/90 px-3 py-2 text-sm text-ink/70 shadow-card backdrop-blur">
          <span>Página {page}</span>
          <div className="flex gap-2">
            {previousHref ? (
              <a href={previousHref} className="rounded-full border border-ink/10 bg-sand px-3 py-1 text-xs font-semibold text-ink">
                Anterior
              </a>
            ) : (
              <span className="rounded-full border border-ink/10 bg-mist px-3 py-1 text-xs font-semibold text-ink/45">
                Anterior
              </span>
            )}
            {nextHref ? (
              <a href={nextHref} className="rounded-full border border-ink/10 bg-sand px-3 py-1 text-xs font-semibold text-ink">
                Seguinte
              </a>
            ) : (
              <span className="rounded-full border border-ink/10 bg-mist px-3 py-1 text-xs font-semibold text-ink/45">
                Seguinte
              </span>
            )}
          </div>
        </div>
      </section>
    </DashboardShell>
  );
}
