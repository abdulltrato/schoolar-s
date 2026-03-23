"use server";

import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

function resolveApiBaseUrl() {
  return (
    process.env.API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

function useSecureCookies() {
  return process.env.NODE_ENV === "production" || process.env.COOKIE_SECURE === "true";
}

function readSetCookieValues(response: Response) {
  const headers = response.headers as Headers & {
    getSetCookie?: () => string[];
  };
  if (typeof headers.getSetCookie === "function") {
    return headers.getSetCookie();
  }

  const single = response.headers.get("set-cookie");
  return single ? [single] : [];
}

function extractCookieValue(setCookieHeaders: string[], cookieName: string) {
  for (const header of setCookieHeaders) {
    const match = header.match(new RegExp(`(?:^|,\\s*)${cookieName}=([^;]+)`));
    if (match) {
      return match[1];
    }
  }

  return null;
}

export async function loginAction(formData: FormData) {
  const username = String(formData.get("username") || "").trim();
  const password = String(formData.get("password") || "");
  const nextPath = String(formData.get("next") || "/");

  const response = await fetch(`${resolveApiBaseUrl()}/api/v1/auth/login/`, {
    method: "POST",
    cache: "no-store",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    redirect(`/login?error=invalid_credentials&next=${encodeURIComponent(nextPath)}`);
  }

  const setCookieHeaders = readSetCookieValues(response);
  const sessionId = extractCookieValue(setCookieHeaders, "sessionid");
  const csrfToken = extractCookieValue(setCookieHeaders, "csrftoken");

  if (!sessionId) {
    redirect(`/login?error=session_setup_failed&next=${encodeURIComponent(nextPath)}`);
  }

  const cookieStore = await cookies();
  cookieStore.set("schoolar_sessionid", sessionId, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: useSecureCookies(),
  });
  if (csrfToken) {
    cookieStore.set("schoolar_csrftoken", csrfToken, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      secure: useSecureCookies(),
    });
  }

  revalidatePath("/", "layout");
  redirect(nextPath);
}

export async function logoutAction() {
  const cookieStore = await cookies();
  const sessionId = cookieStore.get("schoolar_sessionid")?.value;
  const csrfToken = cookieStore.get("schoolar_csrftoken")?.value;

  if (sessionId) {
    await fetch(`${resolveApiBaseUrl()}/api/v1/auth/logout/`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        Cookie: [`sessionid=${sessionId}`, csrfToken ? `csrftoken=${csrfToken}` : ""]
          .filter(Boolean)
          .join("; "),
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
      },
    }).catch(() => undefined);
  }

  cookieStore.delete("schoolar_sessionid");
  cookieStore.delete("schoolar_csrftoken");
  revalidatePath("/", "layout");
  redirect("/login");
}
