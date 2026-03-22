type SectionTitleProps = {
  eyebrow: string;
  title: string;
  description: string;
  inverse?: boolean;
};

export function SectionTitle({
  eyebrow,
  title,
  description,
  inverse = false,
}: SectionTitleProps) {
  const tone = inverse ? "text-sand" : "text-ink";
  const bodyTone = inverse ? "text-sand/78" : "text-ink/70";

  return (
    <div>
      <p className={`text-xs font-semibold uppercase tracking-[0.28em] ${tone}`}>
        {eyebrow}
      </p>
      <h2 className={`mt-3 font-display text-3xl font-semibold ${tone}`}>
        {title}
      </h2>
      <p className={`mt-3 max-w-2xl text-sm leading-6 ${bodyTone}`}>
        {description}
      </p>
    </div>
  );
}
