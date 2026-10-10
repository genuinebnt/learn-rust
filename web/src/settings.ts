// Settings stored on the server: editor fonts (applied as CSS variables the editor theme reads) and the
// app's accent colour (applied as data-accent on <html>; the palettes live in app.css).
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type Accent, type EditorSettings, type Settings } from "./api";

export const DEFAULT_EDITOR: EditorSettings = { font_size: 13, font_family: "Fira Code", vim: false, autocomplete: true, rust_analyzer: true, borrow_lanes: false, live_clippy: true, format_on_pause: false, ligatures: false };

const STACK: Record<string, string> = {
  system: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
};
const stack = (family: string) => STACK[family] ?? `'${family}', ui-monospace, monospace`;

/** Google Fonts families loaded on demand; JetBrains Mono and Fira Code are already in index.html. */
const GOOGLE: Record<string, string> = {
  "Fira Code": "Fira+Code:wght@400;500",
  "IBM Plex Mono": "IBM+Plex+Mono:wght@400;500",
  "Source Code Pro": "Source+Code+Pro:wght@400;500",
  "Roboto Mono": "Roboto+Mono:wght@400;500",
};

export const fontLabel = (family: string) => (family === "system" ? "System monospace" : family);

export function loadFont(family: string) {
  const spec = GOOGLE[family];
  const id = `font-${spec}`;
  if (!spec || document.getElementById(id)) return;
  const link = document.createElement("link");
  link.id = id;
  link.rel = "stylesheet";
  link.href = `https://fonts.googleapis.com/css2?family=${spec}&display=swap`;
  document.head.appendChild(link);
}

export function applyEditor(e: EditorSettings) {
  loadFont(e.font_family);
  const root = document.documentElement.style;
  root.setProperty("--editor-font", stack(e.font_family));
  root.setProperty("--editor-size", `${e.font_size}px`);
  root.setProperty("--editor-line", `${Math.round(e.font_size * 1.55)}px`);
  // Ligatures come from the fonts' contextual alternates; both properties are set so every browser agrees.
  root.setProperty("--editor-ligatures", e.ligatures ? "normal" : "none");
  root.setProperty("--editor-features", e.ligatures ? "normal" : '"liga" 0, "calt" 0');
  window.dispatchEvent(new Event("anneal:editor-font"));
  // A newly loaded web font changes glyph widths once it arrives.
  document.fonts?.ready.then(() => window.dispatchEvent(new Event("anneal:editor-font")));
}

/** The saved editor settings, applied to the page, and a setter that saves them. */
export function useEditorSettings() {
  const qc = useQueryClient();
  const settings = useQuery({ queryKey: ["settings"], queryFn: api.settings, staleTime: Infinity });
  const editor = settings.data?.editor ?? DEFAULT_EDITOR;
  const save = useMutation({
    mutationFn: api.saveEditor,
    onMutate: (next) => {
      const prev = qc.getQueryData<Settings>(["settings"]);
      if (prev) qc.setQueryData<Settings>(["settings"], { ...prev, editor: next });
      return prev;
    },
    onError: (_e, _next, prev) => {
      if (prev) qc.setQueryData(["settings"], prev);
    },
  });
  useEffect(() => applyEditor(editor), [editor.font_family, editor.font_size, editor.ligatures]); // eslint-disable-line react-hooks/exhaustive-deps
  return {
    editor,
    families: settings.data?.font_families ?? [DEFAULT_EDITOR.font_family],
    sizes: settings.data?.font_sizes ?? [10, 24],
    set: (next: EditorSettings) => save.mutate(next),
  };
}

export const ACCENTS: { id: Accent; label: string }[] = [
  { id: "copper", label: "Copper" },
  { id: "rose", label: "Rose" },
  { id: "sky", label: "Sky" },
  { id: "teal", label: "Teal" },
];

const ACCENT_KEY = "anneal-accent";

/** Sets the accent on the page and caches it, so index.html can apply it before first paint. */
export function applyAccent(accent: Accent) {
  const root = document.documentElement;
  if (accent === "copper") delete root.dataset.accent;
  else root.dataset.accent = accent;
  try {
    localStorage.setItem(ACCENT_KEY, accent);
  } catch {
    // Private windows can refuse storage; the server copy still applies after load.
  }
}

/** The saved accent, applied to the page, and a setter that saves it. */
export function useAppearance() {
  const qc = useQueryClient();
  const settings = useQuery({ queryKey: ["settings"], queryFn: api.settings, staleTime: Infinity });
  const accent = settings.data?.appearance.accent;
  const save = useMutation({
    mutationFn: api.saveAppearance,
    onMutate: (next) => {
      const prev = qc.getQueryData<Settings>(["settings"]);
      if (prev) qc.setQueryData<Settings>(["settings"], { ...prev, appearance: next });
      return prev;
    },
    onError: (_e, _next, prev) => {
      if (prev) qc.setQueryData(["settings"], prev);
    },
  });
  useEffect(() => {
    if (accent) applyAccent(accent);
  }, [accent]);
  return { accent: accent ?? "copper", set: (next: Accent) => save.mutate({ accent: next }) };
}

export type PageWidth = "narrow" | "wide";
const WIDTH_KEY = "anneal-width";

const readWidth = (): PageWidth => {
  try {
    return localStorage.getItem(WIDTH_KEY) === "wide" ? "wide" : "narrow";
  } catch {
    return "narrow";
  }
};

/** Sets how wide the main screens are (data-width on <html>) and remembers it in this browser. Reading screens ignore it. */
export function applyWidth(width: PageWidth) {
  if (width === "wide") document.documentElement.dataset.width = "wide";
  else delete document.documentElement.dataset.width;
  try {
    localStorage.setItem(WIDTH_KEY, width);
  } catch {
    // the choice then lasts for this visit only
  }
  window.dispatchEvent(new Event("anneal-width"));
}

// Applied as soon as the module loads, so the first paint already has the chosen width.
if (typeof document !== "undefined" && readWidth() === "wide") document.documentElement.dataset.width = "wide";

/** The page width choice and a setter. */
export function usePageWidth() {
  const [width, setWidth] = useState<PageWidth>(readWidth);
  // the header toggle and the account menu both set it: follow the one that did
  useEffect(() => {
    const sync = () => setWidth(document.documentElement.dataset.width === "wide" ? "wide" : "narrow");
    window.addEventListener("anneal-width", sync);
    return () => window.removeEventListener("anneal-width", sync);
  }, []);
  return {
    width,
    set: (next: PageWidth) => {
      applyWidth(next);
      setWidth(next);
    },
  };
}
