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
  return (
    <article className="rounded-[1.5rem] border border-ink/10 bg-sand p-5">
      <div className="flex items-center justify-between gap-4">
        <h3 className="font-display text-xl font-semibold text-ink">{title}</h3>
        <span
          className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] ${toneClasses[tone]}`}
        >
          {status}
        </span>
      </div>
      <p className="mt-4 text-sm leading-6 text-ink/72">{body}</p>
    </article>
  );
}
