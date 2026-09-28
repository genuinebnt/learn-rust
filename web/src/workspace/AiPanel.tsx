// The AI tab in the workspace's right panel (mockup: docs/design_handoff_anneal/designs/ai-assistant.html).
import { useEffect, useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, aiChat, api, type AiAction, type AiMessage, type AiSource } from "../api";
import { aiMarkdown } from "./aimd";

const ACTIONS: { action: AiAction; label: string; title?: string }[] = [
  { action: "explain_error", label: "Explain this error" },
  { action: "hint", label: "Hint", title: "One nudge, no solution" },
  { action: "complexity", label: "Complexity" },
  { action: "similar", label: "How did I do on similar ones?" },
  { action: "review", label: "Review after solve" },
];

const PROVIDER = { gemini: "Gemini", openai: "OpenAI", anthropic: "Claude" } as const;

type Shown = Pick<AiMessage, "role" | "content" | "sources"> & { key: string; pending?: boolean };

export function AiPanel({ problemId, code, solved }: { problemId: string; code: string; solved: boolean }) {
  const qc = useQueryClient();
  const status = useQuery({ queryKey: ["ai-status"], queryFn: api.aiStatus, staleTime: 60_000 });
  const history = useQuery({ queryKey: ["ai-history", problemId], queryFn: () => api.aiHistory(problemId), enabled: !!status.data?.enabled });
  const [live, setLive] = useState<Shown[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assistedNow, setAssistedNow] = useState(false);
  const abort = useRef<AbortController | null>(null);
  const thread = useRef<HTMLDivElement>(null);

  useEffect(() => () => abort.current?.abort(), []);
  useEffect(() => {
    setLive([]);
    setError(null);
    setAssistedNow(false);
  }, [problemId]);

  const shown: Shown[] = [
    ...(history.data ?? []).map((m) => ({ key: `h${m.id}`, role: m.role, content: m.content, sources: m.sources })),
    ...live,
  ];
  // Follow the answer as it streams in.
  useEffect(() => {
    const t = thread.current;
    if (t) t.scrollTop = t.scrollHeight;
  }, [shown.length, live.at(-1)?.content]);

  const clear = useMutation({
    mutationFn: () => api.aiClear(problemId),
    onSuccess: () => {
      setLive([]);
      qc.invalidateQueries({ queryKey: ["ai-history", problemId] });
    },
  });

  const ask = async (body: { message?: string; action?: AiAction }, label: string) => {
    if (busy) return;
    setBusy(true);
    setError(null);
    const stamp = Date.now();
    setLive((l) => [...l, { key: `u${stamp}`, role: "user", content: label, sources: [] }, { key: `a${stamp}`, role: "assistant", content: "", sources: [], pending: true }]);
    const patch = (f: (m: Shown) => Shown) => setLive((l) => l.map((m) => (m.key === `a${stamp}` ? f(m) : m)));
    abort.current = new AbortController();
    try {
      await aiChat(
        problemId,
        { ...body, code },
        {
          sources: (sources) => patch((m) => ({ ...m, sources })),
          assisted: () => {
            setAssistedNow(true);
            qc.invalidateQueries({ queryKey: ["problem", problemId] });
          },
          chunk: (text) => patch((m) => ({ ...m, content: m.content + text })),
        },
        abort.current.signal,
      );
      patch((m) => ({ ...m, pending: false }));
      // The saved history now has both messages; show it from there.
      await qc.invalidateQueries({ queryKey: ["ai-history", problemId] });
      setLive([]);
    } catch (e) {
      if ((e as Error).name === "AbortError") return;
      setError(e instanceof ApiError ? e.message : "The assistant didn't answer. Is the API running?");
      setLive((l) => l.filter((m) => !(m.key === `a${stamp}` && !m.content)));
    } finally {
      setBusy(false);
    }
  };

  const send = () => {
    const text = draft.trim();
    if (!text) return;
    setDraft("");
    void ask({ message: text }, text);
  };

  if (status.isPending) return <p className="note" style={{ padding: 16 }}>Checking the assistant…</p>;
  if (!status.data?.enabled)
    return (
      <div className="ai-off">
        <b>The AI assistant is off.</b>
        <p>It turns on when a model key is set on the server: <code>GEMINI_API_KEY</code> (or <code>OPENAI_API_KEY</code>, <code>ANTHROPIC_API_KEY</code>). Locally, put it in <code>.env.local</code> and restart; in production, in <code>deploy/.env</code>. docs/AI.md has the details.</p>
      </div>
    );

  const info = status.data.info!;
  return (
    <div className="ai">
      <div className="aihead">
        <span className="prov">
          <span className="dot" style={{ background: "var(--grn)" }} />
          {PROVIDER[info.provider]} · {info.model}
        </span>
        <span className="ctx" title="What answers are grounded in">
          problem · code · last run{solved ? " · reference" : ""} · similar · your stats
        </span>
        {shown.length > 0 && (
          <button className="ai-clear" onClick={() => clear.mutate()} disabled={busy} title="Clear this problem's conversation">
            clear
          </button>
        )}
      </div>
      <div className="chips">
        {ACTIONS.filter((a) => a.action !== "review" || solved).map((a) => (
          <button key={a.action} className={`chip${a.action === "hint" ? " warn" : ""}`} disabled={busy} title={a.title} onClick={() => void ask({ action: a.action }, a.label)}>
            {a.label}
          </button>
        ))}
      </div>
      <div className="thread" ref={thread}>
        {shown.length === 0 && <p className="note">Ask about this problem, your code, your last run, or your patterns. Answers use your history across anneal.</p>}
        {shown.map((m) =>
          m.role === "user" ? (
            <div key={m.key} className="msg-u">
              {m.content}
            </div>
          ) : (
            <div key={m.key} className="msg-a">
              {m.pending && !m.content ? (
                <span className="typing" aria-label="Thinking">
                  <i />
                  <i />
                  <i />
                </span>
              ) : (
                <div className="md ai-md" dangerouslySetInnerHTML={{ __html: aiMarkdown(m.content) }} />
              )}
              {m.sources.length > 0 && <Sources sources={m.sources} />}
            </div>
          ),
        )}
      </div>
      {error && <p className="notice bad ai-err">{error}</p>}
      {!solved && (
        <div className="assist">
          <span aria-hidden="true">●</span>
          <span>
            {assistedNow ? "This attempt is now " : "You haven't solved this yet, so AI help marks this attempt "}
            <b>assisted</b>, the same as a hint. Reviews and readiness stay honest.
          </span>
        </div>
      )}
      <div className="composer">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              send();
            }
          }}
          placeholder="Ask about this problem, your code, or your patterns…"
          rows={2}
          disabled={busy}
        />
        <div className="row">
          <span>⌘↵ send · answers stream in</span>
          {busy ? (
            <button className="send" onClick={() => abort.current?.abort()}>
              Stop
            </button>
          ) : (
            <button className="send" onClick={send} disabled={!draft.trim()}>
              Ask
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function Sources({ sources }: { sources: AiSource[] }) {
  return (
    <div className="src">
      grounded on
      {sources.map((s, i) =>
        s.problem_id ? (
          <Link key={i} className="s1" to="/p/$id" params={{ id: s.problem_id }}>
            {s.label}
          </Link>
        ) : (
          <span key={i} className="s1">
            {s.label}
          </span>
        ),
      )}
    </div>
  );
}
