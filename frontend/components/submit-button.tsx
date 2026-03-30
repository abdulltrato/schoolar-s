"use client";
// Botão de envio que mostra estado pending via useFormStatus.

import { useFormStatus } from "react-dom";

type SubmitButtonProps = {
  idleLabel: string;
  pendingLabel: string;
  className?: string;
};

export function SubmitButton({ idleLabel, pendingLabel, className = "" }: SubmitButtonProps) {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className={`inline-flex items-center justify-center gap-2 rounded-full bg-ink px-4 py-2 text-sm font-semibold text-sand disabled:cursor-not-allowed disabled:opacity-60 ${className}`.trim()}
    >
      {pending ? <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-sand/35 border-t-sand" /> : null}
      {pending ? pendingLabel : idleLabel}
    </button>
  );
}
