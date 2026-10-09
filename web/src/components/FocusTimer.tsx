// A focus timer for the stage page's right panel: Pomodoro (focus and break phases, a long break after the fourth), a countdown (the interview
// clock) and a stopwatch, all on one ring. It lives in the browser only: nothing about it is stored on the server, only the lengths you chose.

import { useEffect, useRef, useState } from "react";
import { getPref, setPref } from "../prefs";

type Mode = "pom" | "timer" | "sw";
type Phase = "focus" | "break" | "long";

interface Cfg {
    mode: Mode;
    focus: number;
    brk: number;
    timer: number;
}

const DEFAULTS: Cfg = { mode: "pom", focus: 25, brk: 5, timer: 45 };
const MODES: [Mode, string][] = [
    ["pom", "POMODORO"],
    ["timer", "TIMER"],
    ["sw", "STOPWATCH"],
];

interface State {
    phase: Phase;
    /** Seconds left (pomodoro, timer) or elapsed (stopwatch). */
    secs: number;
    total: number;
    running: boolean;
    /** Which of the four focus sessions this is, and how many are done. */
    cycle: number;
    done: number;
    /** What just happened, for the status line. */
    note: string;
}

const lengthOf = (c: Cfg, mode: Mode, phase: Phase) => (mode === "timer" ? c.timer : phase === "focus" ? c.focus : phase === "break" ? c.brk : c.brk * 3) * 60;

function fresh(c: Cfg, mode: Mode = c.mode): State {
    const total = mode === "sw" ? 0 : lengthOf(c, mode, "focus");
    return { phase: "focus", secs: mode === "sw" ? 0 : total, total, running: false, cycle: 1, done: 0, note: "" };
}

/** The state `dt` seconds later. A finished phase moves to the next one (pomodoro) or stops (timer). */
export function advance(s: State, dt: number, c: Cfg, mode: Mode): State {
    if (!s.running) return s;
    if (mode === "sw") return { ...s, secs: s.secs + dt };
    const secs = s.secs - dt;
    if (secs > 0) return { ...s, secs };
    if (mode === "timer") return { ...s, secs: 0, running: false, note: "Time is up." };
    if (s.phase === "focus") {
        const done = s.done + 1;
        const phase: Phase = done % 4 === 0 ? "long" : "break";
        const total = lengthOf(c, mode, phase);
        return { ...s, phase, done, secs: total, total, note: phase === "long" ? "Four sessions done. Take a long break." : "Focus session done. Break time." };
    }
    const cycle = s.phase === "long" ? 1 : Math.min(4, s.cycle + 1);
    const total = lengthOf(c, mode, "focus");
    return { ...s, phase: "focus", cycle, done: s.phase === "long" ? 0 : s.done, secs: total, total, note: "Break over. Back to it." };
}

const mmss = (n: number) => `${String(Math.floor(n / 60)).padStart(2, "0")}:${String(Math.floor(n % 60)).padStart(2, "0")}`;

export function FocusTimer() {
    const [cfg, setCfg] = useState<Cfg>(() => ({ ...DEFAULTS, ...getPref<Partial<Cfg>>("focus.cfg", {}) }));
    const [s, setS] = useState<State>(() => fresh(cfg));
    const [settings, setSettings] = useState(false);
    const cfgRef = useRef(cfg);
    cfgRef.current = cfg;
    const last = useRef(0);

    useEffect(() => {
        if (!s.running) return;
        last.current = Date.now();
        const id = setInterval(() => {
            const now = Date.now();
            const dt = (now - last.current) / 1000;
            last.current = now;
            setS((prev) => advance(prev, dt, cfgRef.current, cfgRef.current.mode));
        }, 500);
        return () => clearInterval(id);
    }, [s.running]);

    const save = (next: Cfg) => {
        setCfg(next);
        setPref("focus.cfg", next);
    };
    const setMode = (mode: Mode) => {
        const next = { ...cfg, mode };
        save(next);
        setS(fresh(next, mode));
    };
    const setLen = (key: "focus" | "brk" | "timer", v: number) => {
        const next = { ...cfg, [key]: v };
        save(next);
        // A change shows at once while the timer is stopped; a running one keeps its current phase.
        if (!s.running && s.secs === s.total) setS(fresh(next));
    };

    const sw = cfg.mode === "sw";
    const p = sw ? ((s.secs % 60) / 60) * 100 : s.total ? ((s.total - s.secs) / s.total) * 100 : 0;
    const frac = s.total ? s.secs / s.total : 1;
    const tone = sw ? "" : cfg.mode === "pom" ? (s.phase === "focus" ? "" : " brk") : frac < 0.05 ? " crit" : frac < 0.2 ? " warn" : "";
    const label = sw ? "ELAPSED" : cfg.mode === "timer" ? "REMAINING" : s.phase === "focus" ? `FOCUS ${s.cycle} / 4` : s.phase === "long" ? "LONG BREAK" : "BREAK";
    const fresh0 = sw ? s.secs === 0 : s.secs === s.total;
    // A countdown that ran out offers to start again, not to resume at zero.
    const finished = cfg.mode === "timer" && !s.running && s.secs === 0;

    return (
        <section className={`cx-focus${tone}`} aria-label="Focus timer">
            <h4>
                <span>FOCUS</span>
                <span className="fm" role="group" aria-label="Timer mode">
                    {MODES.map(([m, l]) => (
                        <button key={m} aria-pressed={cfg.mode === m} className={cfg.mode === m ? "on" : ""} onClick={() => setMode(m)}>
                            {l}
                        </button>
                    ))}
                </span>
            </h4>
            <div className="fbody">
                <div className={`fring${s.running ? " run" : ""}`} style={{ "--p": p } as React.CSSProperties} role="timer" aria-label={`${label} ${mmss(s.secs)}`}>
                    <span>
                        <b>{mmss(s.secs)}</b>
                        <small>{label}</small>
                    </span>
                </div>
                <div className="fctl">
                    <button className="kbtn sm" onClick={() => setS((x) => (finished ? { ...fresh(cfg), running: true } : { ...x, running: !x.running, note: "" }))}>
                        {s.running ? "Pause" : finished ? "Restart" : fresh0 ? "Start" : "Resume"}
                    </button>
                    <div className="fbtns">
                        <button aria-label="Reset" title="Reset" onClick={() => setS(fresh(cfg))}>
                            ↺
                        </button>
                        <button aria-label="Skip to the next phase" title="Skip to the next phase" disabled={sw || cfg.mode === "timer"} onClick={() => setS((x) => ({ ...advance({ ...x, running: true }, x.secs + 1, cfg, cfg.mode), running: x.running }))}>
                            ⏭
                        </button>
                        <button aria-label="Settings" aria-expanded={settings} title="Settings" onClick={() => setSettings(!settings)}>
                            ⚙
                        </button>
                    </div>
                </div>
            </div>
            {cfg.mode === "pom" && (
                <div className="fdots" aria-hidden="true">
                    {[1, 2, 3, 4].map((i) => (
                        <i key={i} className={i <= s.done ? "done" : i === s.cycle && s.phase === "focus" ? "cur" : ""} />
                    ))}
                </div>
            )}
            <div className="fnote" role="status" aria-live="polite">
                {s.note || (cfg.mode === "pom" ? `${s.done} pomodoro${s.done === 1 ? "" : "s"} this visit` : sw ? "counts up until you pause it" : "counts down to zero")}
            </div>
            {settings && (
                <div className="fset">
                    <label>
                        <span>Focus</span>
                        <input type="range" min={5} max={60} step={5} value={cfg.focus} onChange={(e) => setLen("focus", +e.target.value)} />
                        <b>{cfg.focus} min</b>
                    </label>
                    <label>
                        <span>Break</span>
                        <input type="range" min={3} max={20} value={cfg.brk} onChange={(e) => setLen("brk", +e.target.value)} />
                        <b>{cfg.brk} min</b>
                    </label>
                    <label>
                        <span>Timer</span>
                        <input type="range" min={5} max={90} step={5} value={cfg.timer} onChange={(e) => setLen("timer", +e.target.value)} />
                        <b>{cfg.timer} min</b>
                    </label>
                </div>
            )}
        </section>
    );
}
