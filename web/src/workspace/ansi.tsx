import type { CSSProperties, ReactNode } from "react";

// rustc's terminal colours (SGR codes) mapped onto the theme, so compiler output reads like a terminal.
const COLOURS: Record<number, string> = {
  31: "var(--bad)", 91: "var(--bad)",
  32: "var(--grn)", 92: "var(--grn)",
  33: "var(--warn)", 93: "var(--warn)",
  34: "var(--fn)", 94: "var(--fn)",
  35: "var(--vio)", 95: "var(--vio)",
  36: "var(--mac)", 96: "var(--mac)",
  37: "var(--fg)", 97: "var(--fg)",
};

/** Renders text containing ANSI SGR escapes (colour and bold) as styled spans. */
export function Ansi({ text }: { text: string }) {
  const out: ReactNode[] = [];
  let style: { color?: string; bold?: boolean } = {};
  const re = /\x1b\[([0-9;]*)m/g;
  let last = 0;
  let m: RegExpExecArray | null;
  const push = (chunk: string) => {
    if (!chunk) return;
    const css: CSSProperties = { color: style.color, fontWeight: style.bold ? 600 : undefined };
    out.push(style.color || style.bold ? <span key={out.length} style={css}>{chunk}</span> : chunk);
  };
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index));
    last = re.lastIndex;
    for (const code of (m[1] || "0").split(";").map(Number)) {
      if (code === 0) style = {};
      else if (code === 1) style = { ...style, bold: true };
      else if (code === 22) style = { ...style, bold: false };
      else if (code === 39) style = { ...style, color: undefined };
      else if (COLOURS[code]) style = { ...style, color: COLOURS[code] };
    }
  }
  push(text.slice(last));
  return <>{out}</>;
}

/** Text with ANSI escapes removed. */
export const stripAnsi = (s: string) => s.replace(/\x1b\[[0-9;]*m/g, "");
