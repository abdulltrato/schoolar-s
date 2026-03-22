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
    <article className="rounded-[0.8rem] border border-ink/10 bg-sand p-2.5">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-display text-sm font-semibold text-ink sm:text-base">{title}</h3>
        <span
          className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] ${toneClasses[tone]}`}
        >
          {status}
        </span>
      </div>
      <p className="mt-2 text-xs leading-4 text-ink/72 sm:text-sm">{body}</p>
    </article>
  );
}
