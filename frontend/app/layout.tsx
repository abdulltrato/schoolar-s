import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AuthStatus } from "@/components/auth-status";
import "./globals.css";

export const metadata: Metadata = {
  title: "Schoolar-S",
  description: "Home dashboard for the SUBSTRATO EDUCATION ecosystem.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthStatus />
        {children}
      </body>
    </html>
  );
}
