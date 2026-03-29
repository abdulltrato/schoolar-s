"use client";

type MenuToggleProps = {
  isOpen: boolean;
  onToggle: () => void;
};

export function MenuToggleButton({ isOpen, onToggle }: MenuToggleProps) {
  return (
    <button
      type="button"
      aria-expanded={isOpen}
      aria-controls="menu-principal"
      aria-label={isOpen ? "Fechar menu" : "Abrir menu"}
      onClick={onToggle}
      className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-[var(--radius-md)] border border-ink/10 bg-white/85 text-ink shadow-sm lg:hidden"
    >
      <span className="relative block h-3.5 w-4">
        <span className={`absolute left-0 top-0 h-[2px] w-4 rounded bg-current transition ${isOpen ? "top-[6px] rotate-45" : ""}`} />
        <span className={`absolute left-0 top-[6px] h-[2px] w-4 rounded bg-current transition ${isOpen ? "opacity-0" : "opacity-100"}`} />
        <span className={`absolute left-0 top-3 h-[2px] w-4 rounded bg-current transition ${isOpen ? "top-[6px] -rotate-45" : ""}`} />
      </span>
    </button>
  );
}
