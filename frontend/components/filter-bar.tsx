type FilterOption = {
  label: string;
  value: string;
};

type FilterField = {
  name: string;
  label: string;
  value: string;
  options: FilterOption[];
};

type FilterBarProps = {
  fields: FilterField[];
};

export function FilterBar({ fields }: FilterBarProps) {
  // Barra de filtros genérica com selects pré-preenchidos e ação submit/limpar.
  return (
    <form className="rounded-[0.9rem] border border-ink/10 bg-white/90 p-2.5 shadow-card backdrop-blur">
      <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
        {fields.map((field) => (
          <label key={field.name} className="block">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-ink/55">
              {field.label}
            </span>
            <select
              name={field.name}
              defaultValue={field.value}
              className="mt-1 w-full rounded-md border border-ink/10 bg-sand px-2.5 py-1.5 text-xs text-ink outline-none transition focus:border-ink/35 sm:text-sm"
            >
              <option value="">Todos</option>
              {field.options.map((option) => (
                <option key={`${field.name}-${option.value}`} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <div className="mt-2 flex gap-1.5">
        <button
          type="submit"
          className="rounded-full bg-ink px-2.5 py-1 text-[11px] font-semibold text-sand sm:text-xs"
        >
          Filtrar
        </button>
        <a
          href="?"
          className="rounded-full border border-ink/10 bg-sand px-2.5 py-1 text-[11px] font-semibold text-ink sm:text-xs"
        >
          Limpar
        </a>
      </div>
    </form>
  );
}
