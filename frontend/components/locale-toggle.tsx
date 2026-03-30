"use client";
// Alterna idioma entre pt e en armazenando preferência no localStorage.

import { useEffect, useState } from "react";

const STORAGE_KEY = "schoolar_locale";

export function LocaleToggle() {
  const [locale, setLocale] = useState<"pt" | "en">("pt");

  useEffect(() => {
    const stored = (localStorage.getItem(STORAGE_KEY) as "pt" | "en" | null) || "pt";
    setLocale(stored);
    document.documentElement.lang = stored;
  }, []);

  const toggle = () => {
    const next = locale === "pt" ? "en" : "pt";
    setLocale(next);
    localStorage.setItem(STORAGE_KEY, next);
    document.documentElement.lang = next;
    document.cookie = `ui_locale=${next}; path=/; SameSite=Lax`;
    window.location.reload();
  };

  return (
    <button
      type="button"
      onClick={toggle}
      className="fixed left-3 bottom-12 z-50 rounded-full border border-ink/10 bg-white/90 px-3 py-1.5 text-xs font-semibold text-ink shadow-card backdrop-blur hover:border-ink/30 hover:bg-sand"
      aria-label="Alternar idioma Português/Inglês"
    >
      {locale === "pt" ? "English" : "Português"}
    </button>
  );
}
