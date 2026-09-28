// The assistant's provider and API key. The key goes to the server, which checks it with a tiny request before
// saving; the browser never gets it back, only its last four characters.
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, api, type AiInfo } from "../api";

const PROVIDERS: { id: AiInfo["provider"]; label: string; placeholder: string; model: string }[] = [
  { id: "gemini", label: "Gemini", placeholder: "AIza…", model: "gemini-2.5-flash" },
  { id: "openai", label: "OpenAI", placeholder: "sk-…", model: "gpt-5.5" },
  { id: "anthropic", label: "Claude", placeholder: "sk-ant-…", model: "claude-sonnet-4-6" },
];

export function AiKeyForm({ onDone }: { onDone?: () => void }) {
  const qc = useQueryClient();
  const config = useQuery({ queryKey: ["ai-config"], queryFn: api.aiConfig });
  const [provider, setProvider] = useState<AiInfo["provider"] | null>(null);
  const [key, setKey] = useState("");
  const [model, setModel] = useState<string | null>(null);
  const current = config.data;
  const chosen = provider ?? current?.provider ?? "gemini";
  const meta = PROVIDERS.find((p) => p.id === chosen)!;
  // Changing only the model keeps the saved key.
  const keepsKey = !key && current?.source === "settings" && current.provider === chosen;

  const done = () => {
    setKey("");
    qc.invalidateQueries({ queryKey: ["ai-status"] });
    qc.invalidateQueries({ queryKey: ["ai-config"] });
    qc.invalidateQueries({ queryKey: ["ai-history"] });
    onDone?.();
  };
  const save = useMutation({
    mutationFn: () => api.aiSaveConfig({ provider: chosen, api_key: key || undefined, model: (model ?? current?.model ?? "") || undefined }),
    onSuccess: done,
  });
  const remove = useMutation({ mutationFn: api.aiDeleteConfig, onSuccess: done });
  const error = (save.error ?? remove.error) as unknown;

  return (
    <form
      className="aikey"
      onSubmit={(e) => {
        e.preventDefault();
        save.mutate();
      }}
    >
      <b>AI assistant</b>
      {current && current.source !== "none" && (
        <p className="aikey-now">
          Using {PROVIDERS.find((p) => p.id === current.provider)?.label} {current.model ? `· ${current.model} ` : ""}· key {current.key_hint}
          {current.source === "environment" ? " (from the server's environment)" : ""}
        </p>
      )}
      <div className="aikey-seg" role="radiogroup" aria-label="Provider">
        {PROVIDERS.map((p) => (
          <button type="button" key={p.id} role="radio" aria-checked={chosen === p.id} className={chosen === p.id ? "on" : ""} onClick={() => setProvider(p.id)}>
            {p.label}
          </button>
        ))}
      </div>
      <label>
        <span>API key</span>
        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder={keepsKey ? `keep the saved key ${current?.key_hint}` : meta.placeholder}
          autoComplete="off"
          spellCheck={false}
        />
      </label>
      <label>
        <span>Model</span>
        <input value={model ?? current?.model ?? ""} onChange={(e) => setModel(e.target.value)} placeholder={`${meta.model} (default)`} spellCheck={false} />
      </label>
      <p className="aikey-note">Stored on anneal's server, never sent back to the browser. It's checked with a tiny request before saving.</p>
      {error ? <p className="notice bad">{error instanceof ApiError ? error.message : "Couldn't reach the server."}</p> : null}
      <div className="aikey-row">
        <button type="submit" className="btn sm go" disabled={save.isPending || (!key && !keepsKey)}>
          {save.isPending ? "Checking the key…" : "Test & save"}
        </button>
        {current?.source === "settings" && (
          <button type="button" className="btn sm" onClick={() => remove.mutate()} disabled={remove.isPending}>
            Remove key
          </button>
        )}
        {onDone && (
          <button type="button" className="aikey-cancel" onClick={onDone}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
