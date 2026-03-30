import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

// Caminhos que exigem sessão autenticada.
const protectedPaths = [
  "/",
  "/management",
  "/curriculum",
  "/assessment",
  "/reports",
  "/learning",
  "/student",
  "/teacher",
  "/finance",
  "/communication",
  "/audit",
];

// Verifica se a rota solicitada é protegida.
function isProtectedPath(pathname: string) {
  return protectedPaths.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  // Páginas públicas ou /login seguem adiante sem bloqueio.
  if (!isProtectedPath(pathname) || pathname === "/login") {
    return NextResponse.next();
  }

  // Se o cookie de sessão existe, permite acesso.
  const hasSessionCookie = Boolean(request.cookies.get("schoolar_sessionid")?.value);
  if (hasSessionCookie) {
    return NextResponse.next();
  }

  // Sem sessão: redireciona para login preservando destino em ?next.
  const loginUrl = new URL("/login", request.url);
  const nextPath = `${pathname}${search || ""}`;
  loginUrl.searchParams.set("next", nextPath);
  return NextResponse.redirect(loginUrl);
}

// Matcher lista as rotas onde o middleware deve atuar.
export const config = {
  matcher: [
    "/",
    "/management/:path*",
    "/curriculum/:path*",
    "/assessment/:path*",
    "/reports/:path*",
    "/learning/:path*",
    "/student/:path*",
    "/teacher/:path*",
    "/finance/:path*",
    "/communication/:path*",
    "/audit/:path*",
    "/login",
  ],
};
