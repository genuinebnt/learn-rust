// The rustc-style diagnostic card: `error[E0502] message`, the labelled spans with their code, and a footer.
// The inline lens after a run and the hover over a rust-analyzer squiggle both use it, so they look the same.
import type { Diagnostic, Level } from "../api";

const LEVEL_COLOUR: Record<Level, string> = { error: "var(--bad)", warning: "var(--warn)", note: "var(--dim)", help: "var(--grn)" };

/** Builds the card's DOM. `lines` is the file's text split into lines, for the span snippets. */
export function diagCard(d: Diagnostic, lines: string[], file = "src/lib.rs"): HTMLElement {
  const el = document.createElement("div");
  el.className = `lens cm-lens lv-${d.level}`;
  const head = document.createElement("div");
  const code = document.createElement("span");
  code.style.cssText = `color:${LEVEL_COLOUR[d.level]};font-weight:600`;
  code.textContent = `${d.level}${d.code ? `[${d.code}]` : ""}`;
  head.append(code, ` ${d.message}`);
  el.append(head);
  const labelled = d.spans.filter((s) => s.file === file && s.label);
  if (labelled.length) {
    const grid = document.createElement("div");
    grid.className = "gr";
    for (const s of labelled) {
      const line = lines[s.line_start - 1] ?? "";
      const text = s.line_start === s.line_end ? line.slice(s.col_start - 1, s.col_end - 1) : line.slice(s.col_start - 1).trim();
      const num = document.createElement("span");
      num.style.color = "var(--dim)";
      num.textContent = `${s.line_start} │`;
      const snip = document.createElement("span");
      snip.style.color = s.primary ? LEVEL_COLOUR[d.level] : "var(--acc)";
      snip.textContent = text.length > 30 ? `${text.slice(0, 28)}…` : text;
      const label = document.createElement("span");
      label.textContent = s.label ?? "";
      grid.append(num, snip, label);
    }
    el.append(grid);
  }
  const foot = document.createElement("small");
  for (const text of [/^E\d{4}$/.test(d.code ?? "") ? `rustc --explain ${d.code}` : d.code?.startsWith("clippy::") ? d.code : null, ...d.notes.slice(0, 1)]) {
    if (!text) continue;
    const s = document.createElement("span");
    s.textContent = text;
    foot.append(s);
  }
  if (foot.childElementCount) el.append(foot);
  return el;
}
