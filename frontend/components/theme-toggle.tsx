"use client";
// Botão flutuante para alternar tema claro/escuro aplicando classe no body.

import { useEffect, useState } from "react";

const STORAGE_KEY = "schoolar_theme";

function applyTheme(theme: "light" | "dark") {
  const body = document.body;
  if (theme === "dark") {
    body.classList.add("dark-mode");
  } else {
    body.classList.remove("dark-mode");
  }
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const stored = (localStorage.getItem(STORAGE_KEY) as "light" | "dark" | null) || "light";
    setTheme(stored);
    applyTheme(stored);
  }, []);

  const toggle = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  };

  return (
    <button
      type="button"
      onClick={toggle}
      className="fixed left-3 bottom-3 z-50 rounded-full border border-ink/10 bg-white/90 px-3 py-1.5 text-xs font-semibold text-ink shadow-card backdrop-blur hover:border-ink/30 hover:bg-sand"
      aria-label="Alternar modo claro/escuro"
    >
      {theme === "light" ? "Modo escuro" : "Modo claro"}
    </button>
  );
}
