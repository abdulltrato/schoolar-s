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
      <p className={`text-[10px] font-semibold uppercase tracking-[0.1em] ${tone}`}>
        {eyebrow}
      </p>
      <h2 className={`mt-1 font-display text-lg font-semibold ${tone} sm:text-xl`}>
        {title}
      </h2>
      <p className={`mt-1 max-w-3xl text-xs leading-4 ${bodyTone} sm:text-sm`}>
        {description}
      </p>
    </div>
  );
}
