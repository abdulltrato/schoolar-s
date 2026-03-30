import Link from "next/link";

import { logoutAction } from "@/app/auth/actions";
import { getAuthSession } from "@/lib/api";

export async function AuthStatus() {
  // Recupera sessão no servidor para exibir status de autenticação.
  const session = await getAuthSession();

  // Quando não autenticado, mostra CTA para login.
  if (!session.authenticated || !session.user) {
    return (
      <div className="fixed right-3 top-3 z-50 flex items-center gap-2 rounded-full border border-white/60 bg-[linear-gradient(135deg,rgba(255,255,255,0.95),rgba(247,243,233,0.92))] px-3 py-1.5 text-xs text-ink shadow-card backdrop-blur">
        <span className="text-ink/65">Sem sessão iniciada</span>
        <Link href="/login" className="rounded-full bg-ink px-2.5 py-1 font-semibold text-sand">
          Entrar
        </Link>
      </div>
    );
  }

  // Quando autenticado, exibe usuário e botão de logout com ação server-side.
  return (
    <div className="fixed right-3 top-3 z-50 flex items-center gap-2 rounded-full border border-white/60 bg-[linear-gradient(135deg,rgba(255,255,255,0.95),rgba(247,243,233,0.92))] px-3 py-1.5 text-xs text-ink shadow-card backdrop-blur">
      <span className="text-ink/75">
        {session.user.username} {session.user.role ? `| ${session.user.role}` : ""}
      </span>
      <form action={logoutAction}>
        <button type="submit" className="rounded-full bg-ink px-2.5 py-1 font-semibold text-sand">
          Sair
        </button>
      </form>
    </div>
  );
}
