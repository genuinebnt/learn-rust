import type { ReactNode } from "react";
import type { Band, Mode, Progress } from "../api";

export const BAND_LABEL: Record<Band, string> = { easy: "EASY", medium: "MEDIUM", hard: "HARD" };

/** Difficulty colour: easy green, medium amber, hard red (tokens in app.css). */
export const LEVEL_COLOR: Record<Band, string> = { easy: "var(--lv-easy)", medium: "var(--lv-medium)", hard: "var(--lv-hard)" };

/** A difficulty label with its colour dot. */
export function Level({ level, upper }: { level: Band; upper?: boolean }) {
  return (
    <span style={{ color: LEVEL_COLOR[level], whiteSpace: "nowrap" }}>
      <i className="lvl-dot" style={{ background: LEVEL_COLOR[level] }} />
      {upper ? BAND_LABEL[level] : level}
    </span>
  );
}

/** Section header: mono label, rule, right-aligned caption. */
export function Sech({ title, caption }: { title: ReactNode; caption?: ReactNode }) {
  return (
    <div className="sech">
      <span className="t">{title}</span>
      <span className="rule" />
      {caption !== undefined && <span className="c">{caption}</span>}
    </div>
  );
}

export type PhaseKind = "done" | "cur" | "open" | "ahead" | "vio";

export function Phase({ kind, children, width }: { kind: PhaseKind; children: ReactNode; width?: string }) {
  return (
    <div className={`phase ${kind}`} style={width ? { width } : undefined}>
      {children}
    </div>
  );
}

/** One 4px segment per item; the first `filled` are coloured. */
export function Segs({ n, filled, color = "var(--grn)" }: { n: number; filled: number; color?: string }) {
  return (
    <div className="segs" style={{ gridTemplateColumns: `repeat(${Math.max(n, 1)}, 1fr)` }}>
      {Array.from({ length: n }, (_, i) => (
        <span key={i} style={{ background: i < filled ? color : "var(--line2)" }} />
      ))}
    </div>
  );
}

const MODE: Record<Mode, [string, string]> = {
  write: ["WRITE IT", "var(--acc)"],
  fix: ["FIX THIS", "var(--vio)"],
  stage: ["STAGE", "var(--grn)"],
};

export function ModeTag({ mode }: { mode: Mode }) {
  const [label, color] = MODE[mode];
  return (
    <span className="mode" style={{ color, borderColor: color }}>
      {label}
    </span>
  );
}

export function modeColor(mode: Mode) {
  return MODE[mode][1];
}

const PROGRESS: Record<Progress, [string, string, string]> = {
  not_started: ["not started", "var(--line)", "transparent"],
  started: ["in progress", "var(--acc)", "linear-gradient(90deg,var(--acc) 50%,transparent 50%)"],
  solved: ["solved", "var(--grn)", "var(--grn)"],
  assisted: ["solved, assisted", "var(--grn)", "linear-gradient(135deg,var(--grn) 50%,transparent 50%)"],
};

/** Status as a shape, so it reads without colour: empty box, half box, filled tick, dashed box (not written yet). */
export function StatusIcon({ progress, draft = false, color }: { progress: Progress; draft?: boolean; color?: string }) {
  const label = draft ? "not written" : PROGRESS[progress][0];
  const c = color ?? "currentColor";
  return (
    <svg className="sicon" viewBox="0 0 16 16" width="15" height="15" role="img" aria-label={label} style={{ color: c }}>
      <title>{label}</title>
      {draft ? (
        <rect x="2.5" y="2.5" width="11" height="11" rx="3" fill="none" stroke="currentColor" strokeWidth="1.5" strokeDasharray="2.2 2" />
      ) : progress === "solved" || progress === "assisted" ? (
        <>
          <rect x="2" y="2" width="12" height="12" rx="3" fill="currentColor" opacity={progress === "assisted" ? 0.75 : 1} />
          <path d="M5 8.3l2 2 4-4.3" fill="none" stroke="var(--panel)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </>
      ) : (
        <>
          <rect x="2.5" y="2.5" width="11" height="11" rx="3" fill="none" stroke="currentColor" strokeWidth="1.5" />
          {progress === "started" && <path d="M8 2.5a5.5 5.5 0 0 1 0 11z" fill="currentColor" />}
        </>
      )}
    </svg>
  );
}

export const progressLabel = (p: Progress) => PROGRESS[p][0];

/** Colour for a readiness-style percentage: ≥ 70 green, 40–69 copper, < 40 red. */
export const pctColor = (v: number) => (v >= 70 ? "var(--grn)" : v >= 40 ? "var(--acc)" : "var(--bad)");

export const pad2 = (n: number) => String(n).padStart(2, "0");
