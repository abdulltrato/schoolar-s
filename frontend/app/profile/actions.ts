"use server";

import { revalidatePath } from "next/cache";
import { handleMutationRedirectTo } from "@/lib/api";
import { changePassword, updateProfile } from "@/lib/api";

export async function updateProfileAction(formData: FormData) {
  // Normaliza payload do formulário de perfil.
  const first_name = String(formData.get("first_name") || "").trim();
  const last_name = String(formData.get("last_name") || "").trim();
  const avatar_url = String(formData.get("avatar_url") || "").trim();

  const result = await updateProfile({ first_name, last_name, avatar_url });
  revalidatePath("/profile");
  await handleMutationRedirectTo(result, "/profile", "perfil_atualizado", "perfil_erro");
}

export async function changePasswordAction(formData: FormData) {
  // Processa troca de palavra-passe.
  const old_password = String(formData.get("old_password") || "");
  const new_password = String(formData.get("new_password") || "");

  const result = await changePassword({ old_password, new_password });
  if (result.ok) {
    await handleMutationRedirectTo(result, "/profile", "senha_atualizada", "senha_atualizada");
    return;
  }

  const detail = encodeURIComponent(result.error || "Erro ao alterar a palavra-passe.");
  await handleMutationRedirectTo(result, `/profile?detail=${detail}`, "senha_atualizada", "senha_erro");
}
