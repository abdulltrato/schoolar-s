type MetricCardProps = {
  label: string;
  value: string;
  detail: string;
};

export function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <article className="group relative overflow-hidden rounded-[1.25rem] border border-white/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.95),rgba(247,243,233,0.92))] p-4 shadow-card transition hover:-translate-y-0.5">
      <div aria-hidden className="absolute inset-x-4 top-0 h-px bg-[linear-gradient(90deg,transparent,rgba(20,33,61,0.2),transparent)]" />
      <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/48">
        {label}
      </p>
      <h3 className="mt-3 font-display text-3xl font-semibold text-ink sm:text-[2rem]">
        {value}
      </h3>
      <p className="mt-3 text-sm leading-6 text-ink/68">{detail}</p>
      <div className="mt-4 flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.12em] text-ink/42">
        <span className="h-2 w-2 rounded-full bg-ember transition group-hover:bg-fern" />
        Indicador atualizado
      </div>
    </article>
  );
}
