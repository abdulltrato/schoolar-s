import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

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

function isProtectedPath(pathname: string) {
  return protectedPaths.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (!isProtectedPath(pathname) || pathname === "/login") {
    return NextResponse.next();
  }

  const hasSessionCookie = Boolean(request.cookies.get("schoolar_sessionid")?.value);
  if (hasSessionCookie) {
    return NextResponse.next();
  }

  const loginUrl = new URL("/login", request.url);
  const nextPath = `${pathname}${search || ""}`;
  loginUrl.searchParams.set("next", nextPath);
  return NextResponse.redirect(loginUrl);
}

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
