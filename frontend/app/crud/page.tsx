import { redirect } from "next/navigation";

import { DashboardShell } from "@/components/dashboard-shell";
import { SectionTitle } from "@/components/section-title";
import {
  handleMutationRedirect,
  mutateRecord,
  requireAuthSession,
} from "@/lib/api";

import { CrudConsole } from "./CrudConsole";
import { crudResources } from "./resources";

type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

const panelClass =
  "relative overflow-hidden rounded-[1.1rem] border border-white/70 bg-white/95 p-5 shadow-[0_18px_55px_rgba(20,33,61,0.08)]";

async function handleCrudAction(formData: FormData) {
  "use server";

  const resourceKey = String(formData.get("resource") || "").trim();
  const operation = String(formData.get("operation") || "create").trim();
  const recordId = String(formData.get("record_id") || "").trim();
  const payloadRaw = String(formData.get("payload") || "").trim();

  const resource = crudResources.find((item) => item.key === resourceKey);
  if (!resource) {
    redirect("/crud?status=crud-unknown-resource");
  }

  if (operation !== "create" && !recordId) {
    redirect("/crud?status=crud-missing-id");
  }

  let payload: Record<string, unknown> = {};
  if (operation !== "delete") {
    try {
      payload = payloadRaw ? (JSON.parse(payloadRaw) as Record<string, unknown>) : {};
    } catch {
      redirect("/crud?status=crud-invalid-json");
    }
  }

  const method = operation === "create" ? "POST" : operation === "update" ? "PATCH" : "DELETE";
  const path = operation === "create" ? resource.endpoint : `${resource.endpoint}${recordId}/`;
  const result = await mutateRecord(path, method, payload);

  const successStatus =
    operation === "create"
      ? "crud-created"
      : operation === "update"
        ? "crud-updated"
        : "crud-deleted";

  await handleMutationRedirect(result, "/crud", successStatus, "crud-error");
}

export default async function CrudPage({ searchParams }: PageProps) {
  await requireAuthSession("/crud");
  const params = (await searchParams) || {};
  const status = Array.isArray(params.status) ? params.status[0] : params.status;

  return (
    <DashboardShell
      title="Console CRUD"
      description="Camada operacional para criar, atualizar e remover entidades diretamente nos servicos do Schoolar."
      aside={(
        <>
          <section className="overflow-hidden rounded-[1.35rem] border border-white/40 bg-[linear-gradient(180deg,rgba(32,52,85,0.98),rgba(20,33,61,0.94))] p-5 shadow-card text-sand">
            <SectionTitle
              eyebrow="Operacao"
              title="Centro de comandos"
              description="Execute alteracoes completas com controlo manual sobre payloads e endpoints."
            />
            <dl className="mt-5 space-y-4 text-sm leading-6 text-sand/80">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Recursos</dt>
                <dd className="text-lg font-semibold">{crudResources.length} catalogados</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Operacoes</dt>
                <dd className="text-lg font-semibold">Criar / Atualizar / Apagar</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.16em] text-sand/70">Nota</dt>
                <dd className="text-sm">Confirme tenant e IDs antes de submeter.</dd>
              </div>
            </dl>
          </section>
        </>
      )}
    >
      <section className={panelClass}>
        <SectionTitle
          eyebrow="CRUD"
          title="Executar operacoes completas"
          description="Selecione o recurso, informe o payload JSON e execute a operacao desejada."
        />
        <CrudConsole resources={crudResources} action={handleCrudAction} />
      </section>

      {status ? (
        <section
          className={`mt-4 rounded-[0.9rem] border px-3 py-2 text-sm ${
            status === "crud-error" || status === "crud-invalid-json" || status === "crud-missing-id" || status === "crud-unknown-resource"
              ? "border-ember/20 bg-ember/10 text-ember"
              : "border-fern/20 bg-fern/10 text-fern"
          }`}
        >
          {status === "crud-created" && "Registo criado com sucesso."}
          {status === "crud-updated" && "Registo atualizado com sucesso."}
          {status === "crud-deleted" && "Registo removido com sucesso."}
          {status === "crud-error" && "Nao foi possivel concluir a operacao."}
          {status === "crud-invalid-json" && "O JSON enviado nao e valido."}
          {status === "crud-missing-id" && "Informe o ID do registo para atualizar ou apagar."}
          {status === "crud-unknown-resource" && "Recurso nao reconhecido."}
        </section>
      ) : null}

      <section className="mt-6 rounded-[1.1rem] border border-white/70 bg-white/85 p-4 text-sm text-ink/70 shadow-card">
        <p className="font-semibold text-ink">Dica rapida</p>
        <p className="mt-2 leading-6">
          Use os dashboards tematicos para consultar dados existentes e recolher IDs.
          Os campos com tenant podem ser resolvidos automaticamente se o header estiver configurado.
        </p>
      </section>
    </DashboardShell>
  );
}
