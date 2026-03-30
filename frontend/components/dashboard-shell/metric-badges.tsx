"use client";

type MetricBadgesProps = {
  items: { label: string; value: string }[];
};

export function MetricBadges({ items }: MetricBadgesProps) {
  // Oculta se não houver badges a exibir.
  if (!items || items.length === 0) return null;

  return (
    <div className="grid shrink-0 grid-cols-3 gap-2 text-center">
      {items.map((item) => (
        <div key={item.label} className="rounded-[1rem] border border-ink/10 bg-white/72 px-3 py-2.5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink/45">{item.label}</p>
          <p className="mt-1 font-display text-lg font-semibold text-ink">{item.value}</p>
        </div>
      ))}
    </div>
  );
}
