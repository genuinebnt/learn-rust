import { useMutation, useQueryClient } from "@tanstack/react-query";
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
      say(`${p.title}: ${SAID[grade]}. Back for review ${today ? niceDate(r.due, today) : r.due}.`);
      for (const key of ["dsa", "activity", "tracks", "reviews", "progress", "stats"]) void qc.invalidateQueries({ queryKey: [key] });
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

/** Company pills, the ones asked in the last six months highlighted, the rest behind a "+n" you can hover. */
export function Companies({ companies, limit = 5 }: { companies: DsaCompany[]; limit?: number }) {
  if (!companies.length) return null;
  const rest = companies.slice(limit);
  return (
    <div className="d-cos">
      {companies.slice(0, limit).map((c) => (
        <span key={c.name} className={`d-co${c.recent ? " hot" : ""}`} title={c.recent ? `${c.name}: asked in the last six months` : c.name}>
          {c.name}
        </span>
      ))}
      {rest.length > 0 && (
        <span className="d-co more" title={rest.map((c) => c.name).join(", ")}>
          +{rest.length}
        </span>
      )}
    </div>
  );
}
