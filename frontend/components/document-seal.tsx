type DocumentSealProps = {
  code: string;
  hash: string;
  size?: number;
};

// Lê par de caracteres hex a partir do hash/código.
function pairAt(source: string, index: number) {
  const normalized = source.replace(/[^a-fA-F0-9]/g, "").padEnd(24, "0");
  return normalized.slice(index * 2, index * 2 + 2);
}

export function DocumentSeal({ code, hash, size = 112 }: DocumentSealProps) {
  // Gera um selo pseudo-aleatório com base no código e hash para visualização.
  const seed = `${code}${hash}`;
  const cells = Array.from({ length: 25 }, (_, index) => {
    const value = parseInt(pairAt(seed, index), 16);
    return value % 3 !== 0;
  });
  const cellSize = Math.floor(size / 7);
  const offset = Math.floor((size - cellSize * 5) / 2);

  return (
    <div className="inline-flex flex-col items-center gap-2 rounded-[1rem] border border-ink/10 bg-white px-3 py-3 shadow-card">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-label={`Selo ${code}`} role="img">
        <rect x="0" y="0" width={size} height={size} rx="18" fill="#f7f3e9" />
        <circle cx={size / 2} cy={size / 2} r={(size / 2) - 8} fill="none" stroke="#14213d" strokeWidth="2" strokeDasharray="4 4" />
        {cells.map((active, index) => {
          if (!active) {
            return null;
          }
          const column = index % 5;
          const row = Math.floor(index / 5);
          return (
            <rect
              key={`cell-${index + 1}`}
              x={offset + (column * cellSize)}
              y={offset + (row * cellSize)}
              width={cellSize - 3}
              height={cellSize - 3}
              rx="3"
              fill={index % 2 === 0 ? "#14213d" : "#d96c06"}
            />
          );
        })}
        <circle cx={size / 2} cy={size / 2} r="8" fill="#3c7a57" />
      </svg>
      <div className="text-center">
        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-ink/55">Selo de emissão</p>
        <p className="mt-1 text-[11px] font-semibold text-ink">{code}</p>
      </div>
    </div>
  );
}
