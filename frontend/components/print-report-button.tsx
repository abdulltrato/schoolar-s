"use client";
// Botão simples que chama print() no browser.

export function PrintReportButton() {
  return (
    <button
      type="button"
      onClick={() => window.print()}
      className="rounded-full border border-ink/10 bg-sand px-3 py-1.5 text-xs font-semibold text-ink transition hover:border-ink/30 hover:bg-white"
    >
      Imprimir documento
    </button>
  );
}
