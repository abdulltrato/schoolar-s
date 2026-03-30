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
  // Lista genérica com cabeçalho e contador; aceita render prop para linhas.
  return (
    <article className="rounded-[0.9rem] border border-ink/10 bg-sand p-2.5 sm:p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-display text-base font-semibold text-ink sm:text-lg">{title}</h3>
          <p className="mt-1 text-xs leading-4 text-ink/70 sm:text-sm">{subtitle}</p>
        </div>
        <span className="rounded-full border border-ink/10 bg-white px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/70">
          {snapshot.count}
        </span>
      </div>

      <p className="mt-2 text-xs leading-4 text-ink/70 sm:text-sm">{snapshot.message}</p>

      <div className="mt-2.5 space-y-2">
        {rows.length > 0 ? (
          rows.map(renderRow)
        ) : (
          <div className="rounded-[0.8rem] border border-dashed border-ink/15 px-2.5 py-3 text-xs leading-4 text-ink/55 sm:text-sm">
            Nada para mostrar nesta secção.
          </div>
        )}
      </div>
    </article>
  );
}
