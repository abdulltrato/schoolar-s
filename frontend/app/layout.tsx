import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AuthStatus } from "@/components/auth-status";
import { ThemeToggle } from "@/components/theme-toggle";
import { LocaleToggle } from "@/components/locale-toggle";
import "./globals.css";

// Layout raiz da aplicação Next, aplica AuthStatus global e define metadados.
export const metadata: Metadata = {
  title: "Schoolar-S",
  description: "Painel operacional do ecossistema SUBSTRATO EDUCAÇÃO.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="pt">
      <body>
        <AuthStatus />
        <LocaleToggle />
        <ThemeToggle />
        {children}
      </body>
    </html>
  );
}
