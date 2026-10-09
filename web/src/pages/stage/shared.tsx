// Small pieces the stage page's parts share: how long ago, the stage length estimate and the three difficulty bars.

import type { StageDifficulty } from "../../api";

export function ago(iso: string) {
    const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (s < 60) return "just now";
    if (s < 3600) return `${Math.floor(s / 60)} min ago`;
    if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
    return `${Math.floor(s / 86400)} d ago`;
}

export const DIFFICULTY_LABEL = { "very-easy": "VERY EASY", easy: "EASY", medium: "MEDIUM", hard: "HARD" } as const;

/** The stage length the course page promises per difficulty, in minutes (nothing about a stage's length is measured). */
export const STAGE_MINUTES: Record<StageDifficulty, number> = { "very-easy": 5, easy: 10, medium: 45, hard: 60 };

/** The mockup's difficulty bars: e (one lit, green), m (two, amber), h (three, red). */
export const dClass = (d: StageDifficulty) => (d === "hard" ? "h" : d === "medium" ? "m" : "e");

export function Bars({ d }: { d: StageDifficulty }) {
    return (
        <span className={`k-dd k-${dClass(d)}`} title={d} aria-label={d}>
            <s />
            <s />
            <s />
        </span>
    );
}
