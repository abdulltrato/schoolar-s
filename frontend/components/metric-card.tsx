type MetricCardProps = {
  label: string;
  value: string;
  detail: string;
};

export function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <article className="rounded-[0.8rem] border border-ink/10 bg-sand p-2.5">
      <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">
        {label}
      </p>
      <h3 className="mt-1 font-display text-base font-semibold text-ink sm:text-lg">
        {value}
      </h3>
      <p className="mt-1 text-xs leading-4 text-ink/70 sm:text-sm">{detail}</p>
    </article>
  );
}
