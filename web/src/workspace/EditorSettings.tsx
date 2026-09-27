import { useEffect, useRef, useState, type ReactNode } from "react";
import { DEFAULT_EDITOR, fontLabel, loadFont, useEditorSettings } from "../settings";

/** The "Aa" button in the editor toolbar: font and Vim (saved to your account), plus `children` for this session's editor toggles. */
export function EditorSettingsButton({ children }: { children?: ReactNode }) {
  const { editor, families, sizes, set } = useEditorSettings();
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    // Load every family so each preview renders in its own font.
    families.forEach(loadFont);
    const close = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent ? e.key === "Escape" : !box.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", close);
    return () => {
      document.removeEventListener("mousedown", close);
      document.removeEventListener("keydown", close);
    };
  }, [open, families]);

  const [min, max] = sizes;
  const size = (d: number) => set({ ...editor, font_size: Math.min(max, Math.max(min, editor.font_size + d)) });
  return (
    <div className="eset" ref={box}>
      <button className="eset-btn" aria-expanded={open} aria-haspopup="dialog" title="Editor settings" onClick={() => setOpen(!open)}>
        Aa
      </button>
      {open && (
        <div className="eset-pop" role="dialog" aria-label="Editor settings">
          <h4>EDITOR</h4>
          {children && <div className="eset-session">{children}</div>}
          <div className="eset-row">
            <span>Size</span>
            <span className="eset-step">
              <button onClick={() => size(-1)} disabled={editor.font_size <= min} aria-label="Smaller">
                −
              </button>
              <output aria-live="polite">{editor.font_size}px</output>
              <button onClick={() => size(1)} disabled={editor.font_size >= max} aria-label="Larger">
                +
              </button>
            </span>
          </div>
          <div className="eset-row">
            <span>
              Vim mode
              <small className="eset-hint">jk or kj → normal</small>
            </span>
            <button className={`eset-switch${editor.vim ? " on" : ""}`} role="switch" aria-checked={editor.vim} aria-label="Vim mode" onClick={() => set({ ...editor, vim: !editor.vim })}>
              <i />
            </button>
          </div>
          <div className="eset-fonts" role="radiogroup" aria-label="Font family">
            {families.map((f) => (
              <button
                key={f}
                role="radio"
                aria-checked={editor.font_family === f}
                onClick={() => set({ ...editor, font_family: f })}
              >
                <span>{fontLabel(f)}</span>
                <small style={{ fontFamily: f === "system" ? "ui-monospace, monospace" : `'${f}', monospace` }}>fn ok() {"{}"}</small>
              </button>
            ))}
          </div>
          {(editor.font_size !== DEFAULT_EDITOR.font_size || editor.font_family !== DEFAULT_EDITOR.font_family || editor.vim !== DEFAULT_EDITOR.vim) && (
            <button className="eset-reset" onClick={() => set({ ...editor, font_size: DEFAULT_EDITOR.font_size, font_family: DEFAULT_EDITOR.font_family, vim: DEFAULT_EDITOR.vim })}>
              Reset to defaults
            </button>
          )}
        </div>
      )}
    </div>
  );
}
