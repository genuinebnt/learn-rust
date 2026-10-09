// Small pieces shared by the pages that are built from the mockups (docs/mockups/course-motion.html): the page root that carries the mockup's
// stylesheet (styles/mock-course.css, generated from it), the copy button, and a flag that turns true just after the first paint so bars and
// rings can animate from empty.

import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";

/** True once the page has painted: bars and rings start at 0 and grow to their value. */
export function useReady(): boolean {
    const [ready, setReady] = useState(false);
    useEffect(() => {
        const id = requestAnimationFrame(() => requestAnimationFrame(() => setReady(true)));
        return () => cancelAnimationFrame(id);
    }, []);
    return ready;
}

export const reducedMotion = () => typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/** The root of a page built from the mockup: its stylesheet applies below this, and its entrance motion runs unless motion is reduced. */
export function MockRoot({ children, off = 52, className = "", style, prefix = "k-" }: { children: ReactNode; off?: number; className?: string; style?: CSSProperties; prefix?: string }) {
    return (
        <div className={`${prefix}root${reducedMotion() ? "" : ` ${prefix}motion`} ${className}`} style={{ "--k-off": `${off}px`, "--ease": "cubic-bezier(.22,1,.36,1)", ...style } as CSSProperties}>
            {children}
        </div>
    );
}

/** The mockup's COPY button: says COPIED for a moment. */
export function MockCopy({ text, className = "k-copy" }: { text: string; className?: string }) {
    const [done, setDone] = useState(false);
    useEffect(() => {
        if (!done) return;
        const t = setTimeout(() => setDone(false), 1100);
        return () => clearTimeout(t);
    }, [done]);
    return (
        <button
            type="button"
            className={`${className}${done ? " k-ok" : ""}`}
            onClick={() => {
                try {
                    navigator.clipboard.writeText(text).then(() => setDone(true), () => {});
                } catch {
                    // no clipboard in this context
                }
            }}
        >
            {done ? "COPIED" : "COPY"}
        </button>
    );
}

/** The "rise in" entrance: `--i` is the step in the stagger. */
export const rise = (i: number): { className: string; style: CSSProperties } => ({ className: "k-rv", style: { "--i": i } as CSSProperties });

/** The mockup's grid/list toggle: a thumb that slides under the button that is on. */
export function SlidingSeg<T extends string>({ value, options, onChange, label, prefix = "s-" }: { value: T; options: { key: T; label: ReactNode }[]; onChange: (v: T) => void; label: string; prefix?: string }) {
    const box = useRef<HTMLDivElement>(null);
    const place = () => {
        const on = box.current?.querySelector<HTMLElement>(`button.${prefix}on`);
        const t = box.current?.querySelector<HTMLElement>(`.${prefix}thumb`);
        if (!on || !t) return;
        t.style.width = `${on.offsetWidth}px`;
        t.style.transform = `translateX(${on.offsetLeft - 3}px)`;
    };
    useLayoutEffect(place);
    useEffect(() => {
        addEventListener("resize", place);
        return () => removeEventListener("resize", place);
    });
    return (
        <div className={`${prefix}seg`} ref={box} role="group" aria-label={label}>
            <span className={`${prefix}thumb`} />
            {options.map((o) => (
                <button key={o.key} className={value === o.key ? `${prefix}on` : ""} aria-pressed={value === o.key} onClick={() => onChange(o.key)}>
                    {o.label}
                </button>
            ))}
        </div>
    );
}
