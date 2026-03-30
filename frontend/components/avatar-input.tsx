"use client";

import type { ChangeEvent } from "react";
import { useState } from "react";

type AvatarInputProps = {
  initialUrl?: string;
};

export function AvatarInput({ initialUrl = "" }: AvatarInputProps) {
  // Estado local para manter/prever o avatar enviado.
  const [avatarUrl, setAvatarUrl] = useState(initialUrl);
  const [message, setMessage] = useState("");

  // Atualiza estado e pré-visualização quando o utilizador seleciona um ficheiro.
  const handleFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
      setMessage("Use uma imagem até 2 MB.");
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result?.toString() || "";
      setAvatarUrl(result);
      setMessage("");
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="grid gap-3">
      {/* Campo real enviado ao servidor. */}
      <input type="hidden" name="avatar_url" value={avatarUrl} />

      <div className="flex items-center gap-4">
        <div className="h-16 w-16 overflow-hidden rounded-full border border-ink/10 bg-mist">
          {avatarUrl ? (
            <img src={avatarUrl} alt="Pré-visualização do avatar" className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-[11px] text-ink/50">Sem foto</div>
          )}
        </div>

        <div className="flex-1 space-y-2 text-xs text-ink/70">
          <label className="grid gap-1">
            <span>URL da foto</span>
            <input
              value={avatarUrl}
              onChange={(event) => setAvatarUrl(event.target.value)}
              placeholder="https://cdn.exemplo/avatar.png"
              className="rounded-lg border border-ink/15 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-ink/40 focus:ring-2 focus:ring-mist"
            />
          </label>

          <label className="grid gap-1">
            <span>Ou carregue uma imagem</span>
            <input
              type="file"
              accept="image/*"
              onChange={handleFile}
              className="text-[11px] text-ink/80 file:mr-3 file:rounded-md file:border-0 file:bg-ink file:px-3 file:py-2 file:text-[11px] file:font-semibold file:text-sand"
            />
          </label>
        </div>
      </div>

      {message ? <p className="text-[11px] text-ember">{message}</p> : null}
    </div>
  );
}
