import { useEffect, useRef } from "react";
import { Vim, vim } from "@replit/codemirror-vim";
import { Compartment, EditorState, RangeSetBuilder, StateEffect, StateField, type Extension } from "@codemirror/state";
import {
  Decoration,
  type DecorationSet,
  EditorView,
  ViewPlugin,
  type ViewUpdate,
  WidgetType,
  drawSelection,
  highlightActiveLine,
  highlightActiveLineGutter,
  keymap,
  lineNumbers,
} from "@codemirror/view";
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import { HighlightStyle, bracketMatching, indentOnInput, indentUnit, syntaxHighlighting } from "@codemirror/language";
import { autocompletion, closeBrackets, closeBracketsKeymap, completeAnyWord, completionKeymap } from "@codemirror/autocomplete";
import { rust } from "@codemirror/lang-rust";
import { serverCompletionSource } from "@codemirror/lsp-client";
import { tags as t } from "@lezer/highlight";
import type { Diagnostic } from "../api";
import type { LaneModel } from "./lanes";
import { inlayHints, refreshInlays } from "./inlay";
import type { RaSession } from "./lsp";

const highlight = HighlightStyle.define([
  { tag: [t.keyword, t.self, t.modifier, t.controlKeyword, t.definitionKeyword, t.moduleKeyword], color: "var(--kw)" },
  { tag: [t.typeName, t.className, t.namespace, t.standard(t.typeName)], color: "var(--ty)" },
  { tag: [t.function(t.variableName), t.function(t.propertyName), t.function(t.definition(t.variableName))], color: "var(--fn)" },
  { tag: [t.string, t.character, t.special(t.string)], color: "var(--str)" },
  { tag: [t.number, t.bool, t.atom], color: "var(--num)" },
  { tag: t.macroName, color: "var(--mac)" },
  { tag: [t.labelName, t.special(t.variableName)], color: "var(--lt)" },
  { tag: [t.comment, t.lineComment, t.blockComment, t.docComment], color: "var(--com)" },
]);

const theme = EditorView.theme({
  // Font settings come from the user's editor settings (settings.ts), as CSS variables.
  "&": { height: "100%", backgroundColor: "var(--bg)", color: "var(--fg)", fontSize: "var(--editor-size, 13px)" },
  ".cm-scroller": { fontFamily: "var(--editor-font, var(--mono))", lineHeight: "var(--editor-line, 20px)", position: "relative" },
  ".cm-content": { padding: "12px 0", caretColor: "var(--acc)" },
  ".cm-gutters": { backgroundColor: "var(--bg)", border: "none", color: "var(--dim)" },
  ".cm-lineNumbers .cm-gutterElement": { padding: "0 16px 0 12px", minWidth: "48px" },
  ".cm-activeLine": { backgroundColor: "var(--sel)" },
  ".cm-activeLineGutter": { backgroundColor: "transparent", color: "var(--fg)" },
  ".cm-cursor, .cm-dropCursor": { borderLeftColor: "var(--acc)", borderLeftWidth: "2px" },
  "&.cm-focused .cm-selectionBackground, .cm-selectionBackground, ::selection": {
    backgroundColor: "color-mix(in oklch, var(--acc) 24%, transparent) !important",
  },
  "&.cm-focused": { outline: "none" },
  ".cm-matchingBracket": { backgroundColor: "var(--acc-bg)", color: "inherit" },
  ".cm-tooltip": { backgroundColor: "var(--panel)", border: "1px solid var(--line)", borderRadius: "5px", color: "var(--fg)" },
  ".cm-tooltip-autocomplete ul li": { fontFamily: "var(--mono)", padding: "2px 10px" },
  ".cm-tooltip-autocomplete ul li[aria-selected]": { backgroundColor: "var(--acc-bg)", color: "var(--fg)" },
  ".cm-squig": { textDecoration: "underline wavy var(--bad)", textUnderlineOffset: "4px" },
  ".cm-errline": { backgroundColor: "var(--bad-bg)" },
  ".cm-panels": { backgroundColor: "var(--panel)", color: "var(--mut)", borderTop: "1px solid var(--line2)" },
  ".cm-vim-panel": { padding: "3px 12px", font: "500 11px var(--mono)", minHeight: "22px" },
  ".cm-vim-panel input": { background: "transparent", border: "none", outline: "none", color: "var(--fg)", font: "inherit" },
  ".cm-fat-cursor": { background: "color-mix(in oklch, var(--acc) 70%, transparent) !important", color: "var(--on-acc) !important" },
  "&:not(.cm-focused) .cm-fat-cursor": { background: "none !important", outline: "1px solid var(--acc)" },
});

/* ---------- inline rustc lens ---------- */

class LensWidget extends WidgetType {
  constructor(
    readonly d: Diagnostic,
    readonly lines: string[],
  ) {
    super();
  }
  eq(other: LensWidget) {
    return other.d.rendered === this.d.rendered;
  }
  toDOM() {
    const el = document.createElement("div");
    el.className = "lens cm-lens";
    const head = document.createElement("div");
    const code = document.createElement("span");
    code.style.cssText = "color:var(--bad);font-weight:600";
    code.textContent = `error${this.d.code ? `[${this.d.code}]` : ""}`;
    head.append(code, ` ${this.d.message}`);
    el.append(head);
    const labelled = this.d.spans.filter((s) => s.file === "src/lib.rs" && s.label);
    if (labelled.length) {
      const grid = document.createElement("div");
      grid.className = "gr";
      for (const s of labelled) {
        const line = this.lines[s.line_start - 1] ?? "";
        const text = s.line_start === s.line_end ? line.slice(s.col_start - 1, s.col_end - 1) : line.slice(s.col_start - 1).trim();
        const num = document.createElement("span");
        num.style.color = "var(--dim)";
        num.textContent = `${s.line_start} │`;
        const snip = document.createElement("span");
        snip.style.color = s.primary ? "var(--bad)" : "var(--acc)";
        snip.textContent = text.length > 30 ? `${text.slice(0, 28)}…` : text;
        const label = document.createElement("span");
        label.textContent = s.label ?? "";
        grid.append(num, snip, label);
      }
      el.append(grid);
    }
    const foot = document.createElement("small");
    for (const text of [this.d.code ? `rustc --explain ${this.d.code}` : null, ...this.d.notes.slice(0, 1)]) {
      if (!text) continue;
      const s = document.createElement("span");
      s.textContent = text;
      foot.append(s);
    }
    if (foot.childElementCount) el.append(foot);
    return el;
  }
  ignoreEvent() {
    return false;
  }
}

const setLens = StateEffect.define<Diagnostic[]>();

function lensDecorations(state: EditorState, diagnostics: Diagnostic[]): DecorationSet {
  const doc = state.doc;
  const lines = doc.toString().split("\n");
  const items: { from: number; to: number; deco: Decoration }[] = [];
  const clampLine = (n: number) => doc.line(Math.min(Math.max(n, 1), doc.lines));
  for (const d of diagnostics) {
    const primary = d.spans.find((s) => s.primary && s.file === "src/lib.rs");
    if (!primary) continue;
    const start = clampLine(primary.line_start);
    const end = clampLine(primary.line_end);
    const from = Math.min(start.from + primary.col_start - 1, start.to);
    const to = Math.min(end.from + primary.col_end - 1, end.to);
    items.push({ from: start.from, to: start.from, deco: Decoration.line({ class: "cm-errline" }) });
    if (to > from) items.push({ from, to, deco: Decoration.mark({ class: "cm-squig" }) });
    items.push({ from: end.to, to: end.to, deco: Decoration.widget({ widget: new LensWidget(d, lines), block: true, side: 1 }) });
  }
  items.sort((a, b) => a.from - b.from || a.to - b.to);
  const b = new RangeSetBuilder<Decoration>();
  for (const i of items) b.add(i.from, i.to, i.deco);
  return b.finish();
}

const lensField = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(deco, tr) {
    for (const e of tr.effects) if (e.is(setLens)) return lensDecorations(tr.state, e.value);
    return deco.map(tr.changes);
  },
  provide: (f) => EditorView.decorations.from(f),
});

/* ---------- borrow lanes ---------- */

const setLanes = StateEffect.define<LaneModel | null>();
const lanesField = StateField.define<LaneModel | null>({
  create: () => null,
  update(v, tr) {
    for (const e of tr.effects) if (e.is(setLanes)) return e.value;
    return v;
  },
});

const LANE_X = 18;
const LANE_GAP = 46;

const lanesPlugin = ViewPlugin.fromClass(
  class {
    dom: HTMLDivElement;
    constructor(readonly view: EditorView) {
      this.dom = document.createElement("div");
      this.dom.className = "cm-lanes";
      view.scrollDOM.appendChild(this.dom);
      this.schedule();
    }
    update(u: ViewUpdate) {
      if (u.docChanged || u.geometryChanged || u.viewportChanged || u.transactions.some((t) => t.effects.some((e) => e.is(setLanes)))) this.schedule();
    }
    schedule() {
      this.view.requestMeasure({
        read: (view) => {
          const model = view.state.field(lanesField);
          const doc = view.state.doc;
          const offset = view.documentTop - view.scrollDOM.getBoundingClientRect().top + view.scrollDOM.scrollTop;
          const at = (n: number) => view.lineBlockAt(doc.line(Math.min(Math.max(n, 1), doc.lines)).from);
          const bars = (model?.lanes ?? []).map((l) => ({ lane: l, top: at(l.from).top + offset, bottom: at(l.to).bottom + offset }));
          return { model, bars, height: view.contentHeight + offset, end: at(doc.lines).bottom + offset };
        },
        write: ({ model, bars, height, end }) => this.draw(model, bars, height, end),
      });
    }
    draw(model: LaneModel | null, bars: { lane: LaneModel["lanes"][number]; top: number; bottom: number }[], height: number, end: number) {
      this.dom.replaceChildren();
      this.dom.style.height = `${Math.max(height, end + 140)}px`;
      const color = { scope: "var(--line)", borrow: "var(--acc)", conflict: "var(--bad)" } as const;
      for (const { lane, top, bottom } of bars) {
        const x = LANE_X + lane.column * LANE_GAP;
        const bar = document.createElement("div");
        bar.className = "lbar";
        const h = lane.kind === "conflict" ? 14 : Math.max(bottom - top, 14);
        bar.style.cssText = `left:${x}px;top:${top + (lane.kind === "conflict" ? 3 : 0)}px;height:${h}px;background:${color[lane.kind]}`;
        const label = document.createElement("span");
        label.className = "llab";
        label.style.cssText = `left:${x + 12}px;top:${top + 3}px;color:${lane.kind === "scope" ? "var(--dim)" : color[lane.kind]}`;
        label.textContent = lane.label;
        this.dom.append(bar, label);
        if (lane.kind === "conflict") {
          const link = document.createElement("div");
          link.style.cssText = `position:absolute;left:${x - LANE_GAP + 6}px;top:${top + 9}px;width:${LANE_GAP - 6}px;border-top:1.5px solid var(--bad)`;
          const ring = document.createElement("div");
          ring.style.cssText = `position:absolute;left:${x - 5}px;top:${top + 4}px;width:16px;height:12px;border-radius:50%;box-shadow:0 0 0 4px var(--bad-bg)`;
          this.dom.append(link, ring);
        }
      }
      const note = document.createElement("div");
      note.className = "lnote";
      note.style.top = `${end + 24}px`;
      note.textContent = model ? model.note : "No borrow conflicts in the last run.";
      this.dom.append(note);
    }
    destroy() {
      this.dom.remove();
    }
  },
);

const lanesTheme = EditorView.theme({ ".cm-content": { paddingRight: "260px" } });

/* ---------- component ---------- */

export interface EditorProps {
  /** Replaces the document whenever `docKey` changes. */
  value: string;
  docKey: string;
  readOnly?: boolean;
  /** Vim keybindings (ignored when read-only). */
  vim?: boolean;
  autocomplete?: boolean;
  /** Errors to show inline, for src/lib.rs. */
  diagnostics?: Diagnostic[];
  lanes?: LaneModel | null;
  showLanes?: boolean;
  /** A connected rust-analyzer session: completion, hovers, diagnostics, inlay hints. */
  lsp?: RaSession | null;
  /** Bump to re-fetch inlay hints, e.g. when indexing finishes. */
  lspEpoch?: number;
  onChange?: (code: string) => void;
  onCursor?: (line: number, col: number) => void;
  onRun?: () => void;
  /** Run the scratch main (⌘'). */
  onScratch?: () => void;
  onSubmit?: () => void;
}

// Vim: leave insert mode with `jk` or `kj`, typed within insertModeEscKeysTimeout (200 ms).
Vim.map("jk", "<Esc>", "insert");
Vim.map("kj", "<Esc>", "insert");

export const EDITOR_FONT_EVENT = "anneal:editor-font";

export function Editor(props: EditorProps) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const handlers = useRef(props);
  handlers.current = props;
  const completion = useRef(new Compartment());
  const lanesCompartment = useRef(new Compartment());
  const lspCompartment = useRef(new Compartment());
  const vimCompartment = useRef(new Compartment());

  // Line heights change with the font settings; have CodeMirror re-measure.
  useEffect(() => {
    const remeasure = () => view.current?.requestMeasure();
    window.addEventListener(EDITOR_FONT_EVENT, remeasure);
    return () => window.removeEventListener(EDITOR_FONT_EVENT, remeasure);
  }, []);

  useEffect(() => {
    const run = () => {
      handlers.current.onRun?.();
      return true;
    };
    const submit = () => {
      handlers.current.onSubmit?.();
      return true;
    };
    const scratch = () => {
      handlers.current.onScratch?.();
      return true;
    };
    const extensions: Extension[] = [
      // First, so its keymap wins over the others.
      vimCompartment.current.of([]),
      // rustfmt style: Tab and auto-indent insert 4 spaces; tab characters display 4 wide.
      indentUnit.of("    "),
      EditorState.tabSize.of(4),
      lineNumbers(),
      highlightActiveLineGutter(),
      highlightActiveLine(),
      drawSelection(),
      history(),
      indentOnInput(),
      bracketMatching(),
      closeBrackets(),
      rust(),
      syntaxHighlighting(highlight),
      theme,
      lensField,
      lanesField,
      keymap.of([{ key: "Mod-Enter", run }, { key: "Shift-Mod-Enter", run: submit }, { key: "Mod-'", run: scratch }, ...closeBracketsKeymap, ...completionKeymap, ...defaultKeymap, ...historyKeymap, indentWithTab]),
      completion.current.of([]),
      lspCompartment.current.of([]),
      lanesCompartment.current.of([]),
      EditorView.updateListener.of((u) => {
        if (u.docChanged) handlers.current.onChange?.(u.state.doc.toString());
        if (u.selectionSet || u.docChanged) {
          const pos = u.state.selection.main.head;
          const line = u.state.doc.lineAt(pos);
          handlers.current.onCursor?.(line.number, pos - line.from + 1);
        }
      }),
    ];
    if (props.readOnly) extensions.push(EditorState.readOnly.of(true), EditorView.editable.of(false));
    const v = new EditorView({ parent: host.current!, state: EditorState.create({ doc: props.value, extensions }) });
    view.current = v;
    return () => {
      v.destroy();
      view.current = null;
    };
    // The view is created once; props flow in through the effects below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // A new document (another problem, a reset, a run's code): replace the buffer.
  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== props.value) v.dispatch({ changes: { from: 0, to: v.state.doc.length, insert: props.value } });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.docKey]);

  // Words from the buffer, or rust-analyzer's completions once it's connected.
  useEffect(() => {
    const source = props.lsp ? serverCompletionSource : completeAnyWord;
    view.current?.dispatch({
      effects: completion.current.reconfigure(props.autocomplete ? autocompletion({ override: [source], activateOnTyping: true }) : []),
    });
  }, [props.autocomplete, props.lsp]);

  useEffect(() => {
    const on = !!props.vim && !props.readOnly;
    view.current?.dispatch({ effects: vimCompartment.current.reconfigure(on ? vim({ status: true }) : []) });
  }, [props.vim, props.readOnly]);

  useEffect(() => {
    const lsp = props.lsp;
    view.current?.dispatch({ effects: lspCompartment.current.reconfigure(lsp ? [lsp.client.plugin(lsp.uri, "rust"), inlayHints()] : []) });
  }, [props.lsp]);

  useEffect(() => {
    if (props.lspEpoch) view.current?.dispatch({ effects: refreshInlays.of(null) });
  }, [props.lspEpoch]);

  useEffect(() => {
    view.current?.dispatch({ effects: setLens.of((props.diagnostics ?? []).filter((d) => d.level === "error")) });
  }, [props.diagnostics]);

  useEffect(() => {
    view.current?.dispatch({
      effects: [setLanes.of(props.lanes ?? null), lanesCompartment.current.reconfigure(props.showLanes ? [lanesPlugin, lanesTheme] : [])],
    });
  }, [props.lanes, props.showLanes]);

  return <div className="cmhost" ref={host} />;
}
