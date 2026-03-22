import type { ReactNode } from "react";

import type { CollectionSnapshot } from "@/lib/api";

type RecordListProps<T> = {
  title: string;
  subtitle: string;
  snapshot: CollectionSnapshot<T>;
  rows: T[];
  renderRow: (row: T) => ReactNode;
};

export function RecordList<T>({
  title,
  subtitle,
  snapshot,
  rows,
  renderRow,
}: RecordListProps<T>) {
  return (
    <article className="rounded-[1.5rem] border border-ink/10 bg-sand p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-2xl font-semibold text-ink">{title}</h3>
          <p className="mt-2 text-sm leading-6 text-ink/70">{subtitle}</p>
        </div>
        <span className="rounded-full border border-ink/10 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-ink/70">
          {snapshot.count}
        </span>
      </div>

      <p className="mt-4 text-sm leading-6 text-ink/70">{snapshot.message}</p>

      <div className="mt-5 space-y-3">
        {rows.length > 0 ? (
          rows.map(renderRow)
        ) : (
          <div className="rounded-[1rem] border border-dashed border-ink/15 px-4 py-5 text-sm leading-6 text-ink/55">
            Nada para mostrar nesta secao.
          </div>
        )}
      </div>
    </article>
  );
}
