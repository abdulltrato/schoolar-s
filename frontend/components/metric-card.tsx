type MetricCardProps = {
  label: string;
  value: string;
  detail: string;
};

export function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <article className="rounded-[1.5rem] border border-ink/10 bg-sand p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.25em] text-ink/55">
        {label}
      </p>
      <h3 className="mt-3 font-display text-2xl font-semibold text-ink">
        {value}
      </h3>
      <p className="mt-3 text-sm leading-6 text-ink/70">{detail}</p>
    </article>
  );
}
