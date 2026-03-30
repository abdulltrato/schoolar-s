type StatusCardProps = {
  title: string;
  status: string;
  body: string;
  tone: "success" | "warning";
};

const toneClasses = {
  success: "border-fern/20 bg-fern/10 text-fern",
  warning: "border-ember/20 bg-ember/10 text-ember",
};

export function StatusCard({ title, status, body, tone }: StatusCardProps) {
  // Cartão com selo de status (sucesso/alerta) para mensagens curtas.
  return (
    <article className="relative overflow-hidden rounded-[1.15rem] border border-white/70 bg-white/88 p-4 shadow-card">
      <div aria-hidden className="absolute right-[-1.5rem] top-[-1.5rem] h-16 w-16 rounded-full bg-mist/50 blur-2xl" />
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-display text-base font-semibold text-ink">{title}</h3>
        <span
          className={`rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${toneClasses[tone]}`}
        >
          {status}
        </span>
      </div>
      <p className="mt-3 text-sm leading-6 text-ink/70">{body}</p>
    </article>
  );
}
