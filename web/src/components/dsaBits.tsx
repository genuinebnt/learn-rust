import { useMutation, useQueryClient } from "@tanstack/react-query";
import { marked } from "marked";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { api, type DsaCompany, type DsaProblem, type Grade } from "../api";
import { MARK_GLYPH, markOf, niceDate } from "../dsa";

const SAID: Record<Grade, string> = { good: "on your own", hard: "with help", again: "not yet", easy: "easy" };

/** Logs a problem and says when it comes back. Render `toast` once on the page. */
export function useLogger(today: string | undefined): { log: (p: DsaProblem, grade: Grade) => void; toast: ReactNode; busy: boolean } {
  const qc = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);
  const timer = useRef<number>(0);
  const say = (m: string) => {
    setMessage(m);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setMessage(null), 3200);
  };
  useEffect(() => () => window.clearTimeout(timer.current), []);
  const m = useMutation({
    mutationFn: ({ p, grade }: { p: DsaProblem; grade: Grade }) => api.logDsa(p.id, grade),
    onSuccess: (r, { p, grade }) => {
      say(r.due ? `${p.title}: ${SAID[grade]}. Back for review ${today ? niceDate(r.due, today) : r.due}.` : `${p.title}: ${SAID[grade]}. Practice schedules no review.`);
      for (const key of ["dsa", "practice", "activity", "tracks", "reviews", "progress", "stats"]) void qc.invalidateQueries({ queryKey: [key] });
    },
    onError: (e: Error) => say(`Couldn't log it: ${e.message}`),
  });
  return {
    log: (p, grade) => m.mutate({ p, grade }),
    busy: m.isPending,
    toast: message ? (
      <div className="d-toast" role="status">
        {message}
      </div>
    ) : null,
  };
}

/** The ring that says how the latest log went: ✓ on my own, ½ with help, ✗ not yet. */
export function Mark({ p, today }: { p: DsaProblem; today: string }) {
  const mark = markOf(p);
  const label = p.state.last_grade ? (p.state.due && p.state.due <= today && mark !== "fail" ? "Due for review" : mark === "fail" ? "Couldn't yet" : "Solved") : "Not started";
  return (
    <span className={`d-st ${mark}`} title={label}>
      {MARK_GLYPH[mark]}
    </span>
  );
}

/** Company pills: the ones asked in the last six months highlighted, and "+n" opens the rest in place.
 *  With `onPick`, a pill filters the list by that company. */
export function Companies({ companies, limit = 5, onPick, picked }: { companies: DsaCompany[]; limit?: number; onPick?: (name: string) => void; picked?: ReadonlySet<string> }) {
  const [all, setAll] = useState(false);
  if (!companies.length) return null;
  const shown = all ? companies : companies.slice(0, limit);
  const rest = companies.length - limit;
  return (
    <div className="d-cos">
      {shown.map((c) => {
        const cls = `d-co${c.recent ? " hot" : ""}${picked?.has(c.name) ? " on" : ""}`;
        const title = `${c.recent ? `${c.name}: asked in the last six months` : c.name}${onPick ? " · click to filter" : ""}`;
        return onPick ? (
          <button key={c.name} className={cls} title={title} onClick={() => onPick(c.name)}>
            {c.name}
          </button>
        ) : (
          <span key={c.name} className={cls} title={title}>
            {c.name}
          </span>
        );
      })}
      {rest > 0 && (
        <button className="d-co more" aria-expanded={all} title={all ? "Show fewer" : companies.slice(limit).map((c) => c.name).join(", ")} onClick={() => setAll(!all)}>
          {all ? "show fewer" : `+${rest}`}
        </button>
      )}
    </div>
  );
}

/** Markdown from the content files (ours, so it's trusted), as inline or block HTML. */
export function Md({ text, inline }: { text: string; inline?: boolean }) {
  const html = inline ? marked.parseInline(text, { async: false }) : marked.parse(text, { async: false });
  return inline ? <span dangerouslySetInnerHTML={{ __html: html }} /> : <div className="d-md" dangerouslySetInnerHTML={{ __html: html }} />;
}

const KEYWORDS = "def|class|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|import|from|as|with|yield|lambda|try|except|finally|raise|pass|break|continue|global|nonlocal";
const BUILTINS = "range|len|set|dict|list|tuple|deque|sum|any|all|min|max|enumerate|zip|sorted|print|int|str|self|Counter|defaultdict";
const TOKEN = new RegExp(`(#[^\\n]*)|("""[\\s\\S]*?"""|"(?:[^"\\\\\\n]|\\\\.)*"|'(?:[^'\\\\\\n]|\\\\.)*')|\\b(${KEYWORDS})\\b|\\b(${BUILTINS})\\b|\\b(\\d[\\d_]*)\\b|(\\w+)(?=\\()`, "g");

/** Python with light highlighting and a copy button. */
export function PyCode({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  const parts: ReactNode[] = [];
  let last = 0;
  for (const m of code.matchAll(TOKEN)) {
    const at = m.index ?? 0;
    if (at > last) parts.push(code.slice(last, at));
    const [text, comment, str, kw, builtin, num] = m;
    const cls = comment ? "c" : str ? "s" : kw ? "k" : builtin ? "b" : num ? "n" : "f";
    parts.push(<span key={at} className={`py-${cls}`}>{text}</span>);
    last = at + text.length;
  }
  parts.push(code.slice(last));
  return (
    <div className="d-code">
      <button
        className="d-copy"
        onClick={() => {
          navigator.clipboard.writeText(code).then(
            () => {
              setCopied(true);
              window.setTimeout(() => setCopied(false), 1600);
            },
            () => undefined,
          );
        }}
      >
        {copied ? "copied" : "copy"}
      </button>
      <pre>{parts}</pre>
    </div>
  );
}
