import type { Diagnostic, Span } from "../api";

/** Borrow-checker errors that come with "borrow occurs here / later used here" labels. */
const BORROW_CODES = new Set(["E0499", "E0502", "E0505", "E0506", "E0597", "E0716", "E0503", "E0373"]);

export interface Lane {
  kind: "scope" | "borrow" | "conflict";
  /** 1-based, inclusive. */
  from: number;
  to: number;
  label: string;
  /** Which column the lane is drawn in. */
  column: number;
}

export interface LaneModel {
  lanes: Lane[];
  conflicts: number;
  note: string;
}

const isStart = (l: string) => /borrow(ed)? .*occurs here|borrowed here|value moved here|captured here|first .*borrow/i.test(l) && !/later/i.test(l);
const isLater = (l: string) => /later used|later captured|borrow later|used here, in later/i.test(l);

function snippet(code: string[], s: Span): string {
  const line = code[s.line_start - 1] ?? "";
  const text = s.line_start === s.line_end ? line.slice(s.col_start - 1, s.col_end - 1) : line.slice(s.col_start - 1);
  const t = text.trim();
  return t.length > 26 ? `${t.slice(0, 24)}…` : t;
}

/** The `fn` a line sits in: its signature line, closing line, and receiver if any. */
function enclosingFn(code: string[], line: number): Lane | null {
  for (let i = line - 1; i >= 0; i--) {
    const m = /^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+(\w+)[^(]*\(([^)]*)/.exec(code[i] ?? "");
    if (!m) continue;
    let depth = 0;
    let opened = false;
    for (let j = i; j < code.length; j++) {
      for (const ch of code[j] ?? "") {
        if (ch === "{") {
          depth++;
          opened = true;
        } else if (ch === "}") depth--;
      }
      if (opened && depth <= 0) {
        const recv = /&\s*mut\s+self|&\s*self|\bself\b/.exec(m[2] ?? "");
        return { kind: "scope", from: i + 1, to: j + 1, label: recv ? recv[0].replace(/\s+/g, " ") : `fn ${m[1]}`, column: 0 };
      }
    }
    return null;
  }
  return null;
}

/** Lanes for the borrow errors in a run, or null if there are none. */
export function deriveLanes(diagnostics: Diagnostic[], source: string): LaneModel | null {
  const code = source.split("\n");
  const borrowErrors = diagnostics.filter((d) => d.level === "error" && d.code && BORROW_CODES.has(d.code)).slice(0, 2);
  if (borrowErrors.length === 0) return null;
  const lanes: Lane[] = [];
  borrowErrors.forEach((d, k) => {
    const spans = d.spans.filter((s) => s.file === "src/lib.rs");
    const primary = spans.find((s) => s.primary);
    const starts = spans.filter((s) => !s.primary && s.label && isStart(s.label));
    const later = spans.filter((s) => s.label && isLater(s.label));
    if (!primary) return;
    if (k === 0) {
      const scope = enclosingFn(code, (starts[0] ?? primary).line_start);
      if (scope) lanes.push(scope);
    }
    const col = 1 + k * 2;
    if (starts.length) {
      const from = Math.min(...starts.map((s) => s.line_start));
      const to = Math.max(from, ...later.map((s) => s.line_end), primary.line_start);
      lanes.push({ kind: "borrow", from, to, label: snippet(code, starts[0]!), column: col });
    }
    lanes.push({ kind: "conflict", from: primary.line_start, to: primary.line_end, label: `${snippet(code, primary)} · ${d.code}`, column: col + 1 });
  });
  return { lanes, conflicts: borrowErrors.length, note: borrowErrors[0]!.message };
}
