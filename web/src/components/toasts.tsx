// The mockup's toast stack (docs/mockups/course-motion.html, ".tstack" / ".tt"): a card slides in at the top right, a line runs down along its
// bottom edge for how long it stays, and it can be closed. `toast()` can be called from anywhere.

import { useEffect, useSyncExternalStore } from "react";

export type ToastKind = "ok" | "in" | "er";
export interface ToastItem {
    id: number;
    kind: ToastKind;
    title: string;
    text?: string;
    action?: { label: string; run: () => void };
    leaving?: boolean;
}

let items: ToastItem[] = [];
let next = 1;
const listeners = new Set<() => void>();
const emit = () => listeners.forEach((l) => l());
const ICON: Record<ToastKind, string> = { ok: "✓", in: "i", er: "×" };

function remove(id: number) {
    items = items.map((t) => (t.id === id ? { ...t, leaving: true } : t));
    emit();
    setTimeout(() => {
        items = items.filter((t) => t.id !== id);
        emit();
    }, 300);
}

/** Shows a toast. It stays four seconds (longer with an action), unless it is closed first. */
export function toast(kind: ToastKind, title: string, text?: string, action?: ToastItem["action"]) {
    const id = next++;
    items = [...items.slice(-3), { id, kind, title, text, action }];
    emit();
    setTimeout(() => remove(id), action ? 9000 : 4000);
    return id;
}

/** Mounted once, near the root of the app. */
export function ToastHost() {
    const list = useSyncExternalStore(
        (cb) => (listeners.add(cb), () => listeners.delete(cb)),
        () => items,
    );
    useEffect(() => () => void (items = []), []);
    return (
        <div className="k-root">
            <div className="k-tstack" role="region" aria-label="Notifications" aria-live="polite">
                {list.map((t) => (
                    <div key={t.id} className={`k-tt k-${t.kind}${t.leaving ? " k-out" : ""}`} role="status">
                        <span className="k-i" aria-hidden="true">{ICON[t.kind]}</span>
                        <div>
                            <b>{t.title}</b>
                            {t.text && <span>{t.text}</span>}
                            {t.action && (
                                <button className="k-tact" onClick={() => (t.action?.run(), remove(t.id))}>
                                    {t.action.label}
                                </button>
                            )}
                        </div>
                        <button className="k-q" aria-label="Dismiss" onClick={() => remove(t.id)}>
                            ×
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
