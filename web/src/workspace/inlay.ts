// Inlay type hints from rust-analyzer (`: Vec<u32>` after a `let`), which
// @codemirror/lsp-client doesn't provide itself.
import { RangeSetBuilder, StateEffect, StateField, type Extension } from "@codemirror/state";
import { Decoration, type DecorationSet, EditorView, ViewPlugin, type ViewUpdate, WidgetType } from "@codemirror/view";
import { LSPPlugin } from "@codemirror/lsp-client";

interface InlayHint {
  position: { line: number; character: number };
  label: string | { value: string }[];
  paddingLeft?: boolean;
  paddingRight?: boolean;
}

class HintWidget extends WidgetType {
  constructor(readonly text: string) {
    super();
  }
  eq(o: HintWidget) {
    return o.text === this.text;
  }
  toDOM() {
    const el = document.createElement("span");
    el.className = "ih";
    el.textContent = this.text;
    return el;
  }
}

const setHints = StateEffect.define<DecorationSet>();
/** Dispatch to ask for fresh hints, e.g. once indexing finishes. */
export const refreshInlays = StateEffect.define<null>();

const hintsField = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(d, tr) {
    for (const e of tr.effects) if (e.is(setHints)) return e.value;
    return d.map(tr.changes);
  },
  provide: (f) => EditorView.decorations.from(f),
});

const fetcher = ViewPlugin.fromClass(
  class {
    timer: ReturnType<typeof setTimeout> | undefined;
    constructor(readonly view: EditorView) {
      this.schedule(300);
    }
    update(u: ViewUpdate) {
      if (u.docChanged || u.transactions.some((t) => t.effects.some((e) => e.is(refreshInlays)))) this.schedule(500);
    }
    schedule(ms: number) {
      clearTimeout(this.timer);
      this.timer = setTimeout(() => void this.fetch(), ms);
    }
    async fetch() {
      const lsp = LSPPlugin.get(this.view);
      if (!lsp || !lsp.client.connected) return;
      const doc = this.view.state.doc;
      lsp.client.sync();
      let hints: InlayHint[] | null;
      try {
        hints = await lsp.client.request<unknown, InlayHint[] | null>("textDocument/inlayHint", {
          textDocument: { uri: lsp.uri },
          range: { start: { line: 0, character: 0 }, end: lsp.toPosition(doc.length, doc) },
        });
      } catch {
        return; // e.g. "content modified" while typing; the next change asks again
      }
      if (this.view.state.doc !== doc) return; // stale
      const b = new RangeSetBuilder<Decoration>();
      const items = (hints ?? [])
        .map((h) => ({ pos: lsp.fromPosition(h.position, doc), text: `${h.paddingLeft ? " " : ""}${typeof h.label === "string" ? h.label : h.label.map((p) => p.value).join("")}${h.paddingRight ? " " : ""}` }))
        .sort((a, b) => a.pos - b.pos);
      for (const i of items) b.add(i.pos, i.pos, Decoration.widget({ widget: new HintWidget(i.text), side: 1 }));
      this.view.dispatch({ effects: setHints.of(b.finish()) });
    }
    destroy() {
      clearTimeout(this.timer);
    }
  },
);

export const inlayHints = (): Extension => [hintsField, fetcher];
