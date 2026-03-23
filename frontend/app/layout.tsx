import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AuthStatus } from "@/components/auth-status";
import "./globals.css";

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
        {children}
      </body>
    </html>
  );
}
