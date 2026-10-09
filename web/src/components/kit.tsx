// Shared controls (docs/mockups/course-motion.html, "Components"): the press ripple, a modal that handles focus and Esc, and the
// congratulations popup shown when tests pass.

import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { getPref, setPref } from "../prefs";

/** Buttons that get a ripple where they are pressed. */
const RIPPLE = ".btn, .go, .ebtn, .chip, .kbtn, .tstrip-run, .tc-go, .sreset, .cx-cli button, .cx-rcmd button, .cx-cta, .cx-cont";

/** Call once at start-up: a click on any of those buttons spreads a ripple from the pointer. Returns the function that removes it. */
export function installPressEffects(): () => void {
    const onDown = (e: PointerEvent) => {
        if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        const el = (e.target as HTMLElement | null)?.closest<HTMLElement>(RIPPLE);
        if (!el || (el as HTMLButtonElement).disabled) return;
        el.classList.add("fx-host");
        const r = el.getBoundingClientRect();
        const d = Math.max(r.width, r.height) * 2;
        const rip = document.createElement("span");
        rip.className = "fx-rip";
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

/** A dialog over the page: Esc and a click outside close it, Tab stays inside, and focus goes back to where it was. */
export function Modal({ onClose, labelledBy, children }: { onClose: () => void; labelledBy: string; children: ReactNode }) {
    const box = useRef<HTMLDivElement>(null);
    useEffect(() => {
        const before = document.activeElement as HTMLElement | null;
        box.current?.querySelector<HTMLElement>("[data-autofocus]")?.focus();
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
            if (e.shiftKey && document.activeElement === first) (e.preventDefault(), last.focus());
            else if (!e.shiftKey && document.activeElement === last) (e.preventDefault(), first.focus());
        };
        document.addEventListener("keydown", onKey, true);
        return () => {
            document.removeEventListener("keydown", onKey, true);
            before?.focus?.();
        };
    }, [onClose]);
    return createPortal(
        <div className="kov" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
            <div className="kdlg" role="dialog" aria-modal="true" aria-labelledby={labelledBy} ref={box}>
                {children}
            </div>
        </div>,
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
            <div className="kconf" aria-hidden="true">
                {confetti.map((c, i) => (
                    <i key={i} style={{ "--x": `${c.x}px`, "--y": `${c.y}px`, "--r": `${c.rot}deg`, "--d": c.d, background: c.c } as React.CSSProperties} />
                ))}
            </div>
            <button className="x" onClick={onClose} aria-label="Close">
                ×
            </button>
            <div className="kseal" aria-hidden="true">
                <svg viewBox="0 0 96 96">
                    <circle className="b" cx="48" cy="48" r="42" />
                    <circle className="f" cx="48" cy="48" r="42" />
                    <path d="M30 50l13 13 24-27" />
                </svg>
            </div>
            <h2 id={id}>{title}</h2>
            <p>{message}</p>
            <div className="ksts">
                {stats.map((s) => (
                    <div key={s.label}>
                        <b>{s.value}</b>
                        <span>{s.label}</span>
                    </div>
                ))}
            </div>
            {next && (
                <div className="knxt">
                    <div style={{ flex: 1 }}>
                        <small>{next.kicker}</small>
                        <b>{next.title}</b>
                    </div>
                    {next.badge && <span className="pill">{next.badge}</span>}
                </div>
            )}
            <div className="acts">
                <button className="kbtn lg" data-autofocus onClick={onGo}>
                    {goLabel} <span className="ar">→</span>
                </button>
                <div className="two">
                    <button className="kbtn sec" onClick={onClose}>
                        Stay here
                    </button>
                    {review && (
                        <button className="kbtn sec" onClick={review.onReview}>
                            {review.label}
                        </button>
                    )}
                </div>
            </div>
            <label className="chk">
                <button
                    type="button"
                    role="switch"
                    aria-checked={off}
                    className="ksw"
                    onClick={() => {
                        setOff(!off);
                        setCelebrateOff(!off);
                    }}
                    aria-label="Don't show this again"
                />
                Don't show this again, just tell me
            </label>
        </Modal>
    );
}
