// The stage page's two side panels: widths you can drag (remembered), a collapsed state for each, and on a narrow screen drawers that slide in.

import { useCallback, useEffect, useState } from "react";
import { getPref, setPref } from "../prefs";

export interface Panels {
    l: number;
    r: number;
    /** Left panel shrunk to a rail, right panel hidden. */
    lc: boolean;
    rc: boolean;
}

const DEFAULTS: Panels = { l: 300, r: 300, lc: false, rc: false };
const LIMITS = { l: [250, 480], r: [270, 480] } as const;

export function usePanels() {
    const [p, setP] = useState<Panels>(() => ({ ...DEFAULTS, ...getPref<Partial<Panels>>("stage.panels", {}) }));
    const [drawer, setDrawer] = useState<"l" | "r" | null>(null);
    const [dragging, setDragging] = useState<"l" | "r" | null>(null);
    const update = useCallback((next: Panels) => {
        setP(next);
        setPref("stage.panels", next);
    }, []);

    // ⌘B / Ctrl+B the left panel, ⌘. / Ctrl+. the right one; Escape closes a drawer.
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            const el = document.activeElement as HTMLElement | null;
            if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable)) return;
            if (e.key === "Escape") setDrawer(null);
            if (!(e.metaKey || e.ctrlKey) || e.altKey) return;
            if (e.key === "b") (e.preventDefault(), update({ ...p, lc: !p.lc }));
            if (e.key === ".") (e.preventDefault(), update({ ...p, rc: !p.rc }));
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [p, update]);

    return { p, update, drawer, setDrawer, dragging, setDragging };
}

export type PanelsApi = ReturnType<typeof usePanels>;

/** The thin handle on a panel's inner edge: drag to resize, double-click to go back to the default width. */
export function Resizer({ side, panels }: { side: "l" | "r"; panels: PanelsApi }) {
    const { p, update, dragging, setDragging } = panels;
    const [lo, hi] = LIMITS[side];
    return (
        <div
            className={`k-rz k-${side}${dragging === side ? " k-act" : ""}`}
            role="separator"
            aria-orientation="vertical"
            aria-label={side === "l" ? "Resize the course panel" : "Resize the page panel"}
            aria-valuemin={lo}
            aria-valuemax={hi}
            aria-valuenow={p[side]}
            tabIndex={0}
            title="Drag to resize · double-click to reset"
            onPointerDown={(e) => {
                e.preventDefault();
                const el = e.currentTarget;
                el.setPointerCapture(e.pointerId);
                const x0 = e.clientX;
                const w0 = p[side];
                setDragging(side);
                const move = (ev: PointerEvent) => {
                    const dx = ev.clientX - x0;
                    const w = Math.max(lo, Math.min(hi, w0 + (side === "l" ? dx : -dx)));
                    update({ ...p, [side]: w });
                };
                const up = () => {
                    setDragging(null);
                    el.removeEventListener("pointermove", move);
                    el.removeEventListener("pointerup", up);
                };
                el.addEventListener("pointermove", move);
                el.addEventListener("pointerup", up);
            }}
            onDoubleClick={() => update({ ...p, [side]: DEFAULTS[side] })}
            onKeyDown={(e) => {
                const step = e.shiftKey ? 40 : 10;
                const sign = side === "l" ? 1 : -1;
                if (e.key === "ArrowLeft") update({ ...p, [side]: Math.max(lo, Math.min(hi, p[side] - sign * step)) });
                if (e.key === "ArrowRight") update({ ...p, [side]: Math.max(lo, Math.min(hi, p[side] + sign * step)) });
            }}
        >
            <span className="k-grip" />
        </div>
    );
}
