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
  return (
    <form className="rounded-[1.5rem] border border-ink/10 bg-white/80 p-5 shadow-card backdrop-blur">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {fields.map((field) => (
          <label key={field.name} className="block">
            <span className="text-xs font-semibold uppercase tracking-[0.22em] text-ink/55">
              {field.label}
            </span>
            <select
              name={field.name}
              defaultValue={field.value}
              className="mt-2 w-full rounded-xl border border-ink/10 bg-sand px-3 py-3 text-sm text-ink outline-none transition focus:border-ink/35"
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
      <div className="mt-4 flex gap-3">
        <button
          type="submit"
          className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-sand"
        >
          Filtrar
        </button>
        <a
          href="?"
          className="rounded-full border border-ink/10 bg-sand px-4 py-2 text-sm font-semibold text-ink"
        >
          Limpar
        </a>
      </div>
    </form>
  );
}
