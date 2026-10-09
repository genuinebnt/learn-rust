// Shared controls (docs/mockups/course-motion.html, "Components"): the press ripple, a modal that handles focus and Esc, and the
// congratulations popup shown when tests pass.

import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { getPref, setPref } from "../prefs";
import { MockRoot } from "./mock";

/** Buttons that get a ripple where they are pressed. */
const RIPPLE = ".btn, .go, .ebtn, .chip, .kbtn, .tstrip-run, .tc-go, .sreset, .cx-cli button, .cx-rcmd button, .cx-cta, .cx-cont, .k-fx, .k-cta, .k-copy, .k-ghost";

/** Call once at start-up: a click on any of those buttons spreads a ripple from the pointer. Returns the function that removes it. */
export function installPressEffects(): () => void {
    const onDown = (e: PointerEvent) => {
        if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        const el = (e.target as HTMLElement | null)?.closest<HTMLElement>(RIPPLE);
        if (!el || (el as HTMLButtonElement).disabled) return;
        const mock = el.matches(".k-fx, .k-cta, .k-copy, .k-ghost");
        if (!mock) el.classList.add("fx-host");
        const r = el.getBoundingClientRect();
        const d = Math.max(r.width, r.height) * 2;
        const rip = document.createElement("span");
        rip.className = mock ? "k-rip" : "fx-rip";
        rip.style.cssText = `width:${d}px;height:${d}px;left:${e.clientX - r.left - d / 2}px;top:${e.clientY - r.top - d / 2}px`;
        el.appendChild(rip);
        setTimeout(() => rip.remove(), 650);
    };
    document.addEventListener("pointerdown", onDown);
    return () => document.removeEventListener("pointerdown", onDown);
}

/** "Don't show the popup again, just continue." */
export const celebrateOff = () => getPref("celebrate.off", false);
export const setCelebrateOff = (v: boolean) => setPref("celebrate.off", v);

/** A dialog over the page, in the mockup's own overlay: Esc and a click outside close it, Tab stays inside, and focus goes back to where it was. */
export function Modal({ onClose, labelledBy, children, tone = "" }: { onClose: () => void; labelledBy: string; children: ReactNode; tone?: string }) {
    const box = useRef<HTMLDivElement>(null);
    // The overlay starts hidden and fades in on the next frame, so its entrance (seal, confetti) plays.
    const [on, setOn] = useState(false);
    useEffect(() => {
        const id = requestAnimationFrame(() => setOn(true));
        return () => cancelAnimationFrame(id);
    }, []);
    useEffect(() => {
        const before = document.activeElement as HTMLElement | null;
        const t = setTimeout(() => box.current?.querySelector<HTMLElement>("[data-autofocus]")?.focus(), 250);
        const onKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                e.stopPropagation();
                onClose();
            }
            if (e.key !== "Tab" || !box.current) return;
            const f = [...box.current.querySelectorAll<HTMLElement>("button, a[href], input, [tabindex]:not([tabindex='-1'])")].filter((x) => x.offsetParent !== null);
            const first = f[0];
            const last = f[f.length - 1];
            if (!first || !last) return;
            // Focus that is still behind the dialog (it takes a moment to open) comes in on the first Tab.
            if (!box.current.contains(document.activeElement)) return (e.preventDefault(), first.focus());
            if (e.shiftKey && document.activeElement === first) (e.preventDefault(), last.focus());
            else if (!e.shiftKey && document.activeElement === last) (e.preventDefault(), first.focus());
        };
        document.addEventListener("keydown", onKey, true);
        return () => {
            clearTimeout(t);
            document.removeEventListener("keydown", onKey, true);
            before?.focus?.();
        };
    }, [onClose]);
    return createPortal(
        <MockRoot>
            <div className={`k-ov${on ? " k-on" : ""}`} role="dialog" aria-modal="true" aria-labelledby={labelledBy} onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
                <div className={`k-dlg${tone ? ` k-${tone}` : ""}`} ref={box}>
                    {children}
                </div>
            </div>
        </MockRoot>,
        document.body,
    );
}

const CONFETTI = ["var(--grn)", "var(--acc)", "var(--vio)", "var(--fn)", "var(--warn)"];

export interface CelebrationProps {
    title: string;
    message: string;
    stats: { value: string; label: string }[];
    /** The next thing, if there is one. */
    next?: { kicker: string; title: string; badge?: string };
    goLabel: string;
    onGo: () => void;
    review?: { label: string; onReview: () => void };
    onClose: () => void;
}

/** Tests passed: a ring that draws itself, a little confetti, and the choice of moving on or staying. */
export function Celebration({ title, message, stats, next, goLabel, onGo, review, onClose }: CelebrationProps) {
    const id = useId();
    const confetti = useMemo(
        () =>
            Array.from({ length: 34 }, (_, i) => {
                const a = (i / 34) * Math.PI * 2;
                const r = 110 + Math.random() * 120;
                return { x: Math.cos(a) * r, y: Math.sin(a) * r + 60, rot: Math.round(Math.random() * 720 - 360), d: Math.round(Math.random() * 180), c: CONFETTI[i % CONFETTI.length] };
            }),
        [],
    );
    const [off, setOff] = useState(celebrateOff);
    return (
        <Modal onClose={onClose} labelledBy={id}>
            <div className="k-cfd" aria-hidden="true">
                {confetti.map((c, i) => (
                    <i key={i} style={{ "--x": `${c.x}px`, "--y": `${c.y}px`, "--r": `${c.rot}deg`, "--d": c.d, background: c.c } as React.CSSProperties} />
                ))}
            </div>
            <button className="k-x2" onClick={onClose} aria-label="Close">
                ×
            </button>
            <div className="k-sealw">
                <svg className="k-seal" viewBox="0 0 96 96" aria-hidden="true">
                    <circle className="k-b" cx="48" cy="48" r="42" />
                    <circle className="k-f" cx="48" cy="48" r="42" />
                    <path d="M30 50l13 13 24-27" />
                </svg>
            </div>
            <h4 id={id}>{title}</h4>
            <p>{message}</p>
            <div className="k-sts">
                {stats.map((s) => (
                    <div key={s.label}>
                        <b>{s.value}</b>
                        <span>{s.label}</span>
                    </div>
                ))}
            </div>
            {next && (
                <div className="k-nxt">
                    <div style={{ flex: 1 }}>
                        <small>{next.kicker}</small>
                        <b>{next.title}</b>
                    </div>
                    {next.badge && <span className="k-bdg k-w">{next.badge}</span>}
                </div>
            )}
            <div className="k-acts">
                <button className="k-cta k-lg k-fx" data-autofocus onClick={onGo}>
                    <span className="k-lbl">{goLabel}</span>
                    <span className="k-ar">→</span>
                </button>
                <div className="k-two">
                    <button className="k-cta k-sec k-fx" onClick={onClose}>
                        <span className="k-lbl">Stay here</span>
                    </button>
                    {review && (
                        <button className="k-cta k-sec k-fx" onClick={review.onReview}>
                            <span className="k-lbl">{review.label}</span>
                        </button>
                    )}
                </div>
            </div>
            <label className="k-chk">
                <button
                    type="button"
                    role="switch"
                    aria-checked={off}
                    className={`k-sw${off ? " k-on" : ""}`}
                    onClick={() => {
                        setOff(!off);
                        setCelebrateOff(!off);
                    }}
                    aria-label="Don't show this again"
                />
                Don't show this again, just continue
            </label>
        </Modal>
    );
}

/** A small COPY button that says COPIED for a moment; the clipboard can be refused, which just leaves the label alone. */
export function CopyButton({ text, className = "kcopy" }: { text: string; className?: string }) {
    const [done, setDone] = useState(false);
    const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
    useEffect(() => () => clearTimeout(timer.current), []);
    return (
        <button
            type="button"
            className={className}
            onClick={() => {
                const ok = () => {
                    setDone(true);
                    clearTimeout(timer.current);
                    timer.current = setTimeout(() => setDone(false), 1200);
                };
                try {
                    navigator.clipboard.writeText(text).then(ok, () => {});
                } catch {
                    // no clipboard in this context
                }
            }}
        >
            {done ? "COPIED" : "COPY"}
        </button>
    );
}

/** A number that counts up to `value` the first time it appears (and eases to a new value later). With reduced motion it just shows the value. */
export function CountUp({ value, format = String }: { value: number; format?: (n: number) => string }) {
    const reduced = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
    const [shown, setShown] = useState(reduced ? value : 0);
    const from = useRef(reduced ? value : 0);
    useEffect(() => {
        if (reduced) {
            setShown(value);
            return;
        }
        const start = performance.now();
        const a = from.current;
        let raf = 0;
        const tick = (t: number) => {
            const k = Math.min(1, (t - start) / 900);
            setShown(Math.round(a + (value - a) * (1 - Math.pow(1 - k, 3))));
            if (k < 1) raf = requestAnimationFrame(tick);
            else from.current = value;
        };
        raf = requestAnimationFrame(tick);
        return () => cancelAnimationFrame(raf);
    }, [value, reduced]);
    return <>{format(shown)}</>;
}
