"use client";

import { useMemo, useState } from "react";
import { SubmitButton } from "@/components/submit-button";

import type { CrudResource } from "./resources";

type CrudConsoleProps = {
  resources: CrudResource[];
  action: (formData: FormData) => void;
};

const controlClass =
  "w-full rounded-[1rem] border border-ink/10 bg-sand px-3 py-2 text-sm text-ink shadow-[inset_0_1px_0_rgba(0,0,0,0.05)] outline-none transition placeholder:text-ink/40 focus:border-ink/30 focus:ring-4 focus:ring-mist";

function formatTemplate(template: Record<string, unknown>) {
  return JSON.stringify(template, null, 2);
}

export function CrudConsole({ resources, action }: CrudConsoleProps) {
  const initialResource = resources[0];
  const [resourceKey, setResourceKey] = useState(initialResource?.key ?? "");
  const [operation, setOperation] = useState("create");
  const [payload, setPayload] = useState(
    initialResource ? formatTemplate(initialResource.template) : "{}",
  );

  const selectedResource = useMemo(
    () => resources.find((resource) => resource.key === resourceKey) || resources[0],
    [resourceKey, resources],
  );

  const handleResourceChange = (value: string) => {
    setResourceKey(value);
    const resource = resources.find((item) => item.key === value);
    if (resource) {
      setPayload(formatTemplate(resource.template));
    }
  };

  const handleOperationChange = (value: string) => {
    setOperation(value);
    if (value === "delete") {
      return;
    }
    if (selectedResource) {
      setPayload(formatTemplate(selectedResource.template));
    }
  };

  return (
    <form action={action} className="grid gap-4">
      <div className="grid gap-3 md:grid-cols-[1.1fr_0.9fr]">
        <label className="block">
          <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Recurso</span>
          <select
            name="resource"
            value={resourceKey}
            onChange={(event) => handleResourceChange(event.target.value)}
            className={controlClass}
          >
            {resources.map((resource) => (
              <option key={resource.key} value={resource.key}>
                {resource.label}
              </option>
            ))}
          </select>
          {selectedResource ? (
            <p className="mt-2 text-xs text-ink/60">{selectedResource.description}</p>
          ) : null}
        </label>
        <label className="block">
          <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Operacao</span>
          <select
            name="operation"
            value={operation}
            onChange={(event) => handleOperationChange(event.target.value)}
            className={controlClass}
          >
            <option value="create">Criar</option>
            <option value="update">Atualizar</option>
            <option value="delete">Apagar</option>
          </select>
          <p className="mt-2 text-xs text-ink/60">
            Endpoint: <span className="font-mono text-[11px]">{selectedResource?.endpoint}</span>
          </p>
        </label>
      </div>

      <label className="block">
        <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">ID do registo</span>
        <input
          name="record_id"
          placeholder="Obrigatorio para atualizar ou apagar"
          className={controlClass}
          required={operation !== "create"}
          disabled={operation === "create"}
        />
      </label>

      <label className="block">
        <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">Payload JSON</span>
        <textarea
          name="payload"
          rows={10}
          value={payload}
          onChange={(event) => setPayload(event.target.value)}
          className={`mt-1 w-full font-mono text-[12px] leading-5 ${controlClass}`}
          disabled={operation === "delete"}
        />
      </label>

      <div className="flex flex-wrap items-center gap-3 text-xs text-ink/60">
        <span className="rounded-full border border-ink/10 bg-white px-3 py-1 font-semibold uppercase tracking-[0.1em]">
          {operation === "delete" ? "Sem payload" : "Enviar JSON"}
        </span>
        <span>
          Para atualizar, envie apenas os campos que deseja mudar.
        </span>
      </div>

      <SubmitButton
        idleLabel={operation === "delete" ? "Executar remocao" : "Executar"}
        pendingLabel="A processar..."
        className="w-full px-4 py-3"
      />
    </form>
  );
}
