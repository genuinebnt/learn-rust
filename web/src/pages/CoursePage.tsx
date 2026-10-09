import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState, type CSSProperties } from "react";
import { api, type CourseOverview, type CourseStageRow, type StageDifficulty } from "../api";
import { Header } from "../components/Header";
import { CountUp } from "../components/kit";
import { MockCopy, MockRoot, reducedMotion, useReady } from "../components/mock";
import { getPref, setPref } from "../prefs";

/** The course the Courses nav item opens. */
export const COURSE_ID = "bustub";

export const DIFFICULTY_COLOR: Record<StageDifficulty, string> = {
    "very-easy": "var(--lv-easy)",
    easy: "var(--lv-easy)",
    medium: "var(--lv-medium)",
    hard: "var(--lv-hard)",
};

/** Title like "The LRU-K replacer" stays plain; "Build a DBMS: BusTub in Rust" puts what follows the colon in the course colour. */
export function SplitTitle({ title }: { title: string }) {
    const i = title.indexOf(": ");
    if (i < 0) return <>{title}</>;
    return (
        <>
            {title.slice(0, i + 1)} <span style={{ color: "var(--grn)" }}>{title.slice(i + 2)}.</span>
        </>
    );
}

const BARS: Record<StageDifficulty, number> = { "very-easy": 1, easy: 1, medium: 2, hard: 3 };
const LABEL: Record<StageDifficulty, string> = { "very-easy": "VERY EASY", easy: "EASY", medium: "MEDIUM", hard: "HARD" };

/** The three-bar difficulty mark CodeCrafters uses next to every stage. */
export function DifficultyMark({ d }: { d: StageDifficulty }) {
    return (
        <span className="cx-dm" style={{ color: DIFFICULTY_COLOR[d] }}>
            {LABEL[d]}
            <i className={BARS[d] >= 1 ? "on" : ""} />
            <i className={BARS[d] >= 2 ? "on" : ""} />
            <i className={BARS[d] >= 3 ? "on" : ""} />
        </span>
    );
}

/** How long a stage takes, by its difficulty (the same ranges the terminal shows). */
const EST: Record<StageDifficulty, string> = { "very-easy": "~5 min", easy: "~10 min", medium: "~45 min", hard: "1 h or more" };
const DIF_CLASS: Record<StageDifficulty, string> = { "very-easy": "e", easy: "e", medium: "m", hard: "h" };

type Filter = "all" | "todo" | "done" | "boss";
const FILTERS: [Filter, string][] = [
    ["all", "all"],
    ["todo", "to do"],
    ["done", "passed"],
    ["boss", "boss"],
];

function StageRow({ course, s, current, index }: { course: string; s: CourseStageRow; current: boolean; index: number }) {
    return (
        <Link className={`k-row${current ? " k-cur" : ""}`} style={{ "--k": index } as CSSProperties} to="/courses/$course/$stage" params={{ course, stage: s.id }}>
            <span className={`k-ck${s.state !== "todo" ? " k-ok" : ""}`} aria-label={s.state === "todo" ? "not passed" : s.state === "assisted" ? "passed with help" : "passed"}>
                {s.state !== "todo" ? "✓" : ""}
            </span>
            <span className="k-no">{s.id.split("-")[1]}</span>
            <span>
                {s.title}
                {s.kind === "boss" && <span className="k-boss">BUSTUB TEST</span>}
            </span>
            {current ? <span className="k-next">UP NEXT</span> : <span />}
            <span className={`k-dif k-${DIF_CLASS[s.difficulty]}`}>
                {LABEL[s.difficulty]}
                <i>
                    <s />
                    <s />
                    <s />
                </i>
            </span>
        </Link>
    );
}

export function CoursePage({ course = COURSE_ID }: { course?: string }) {
    // Which modules are open: remembered in this browser; until there is a choice, only the module you are in.
    const [openCodes, setOpenCodes] = useState<string[] | null>(() => getPref<string[] | null>("course.open", null));
    const [filter, setFilter] = useState<Filter>("all");
    const [find, setFind] = useState("");
    const findBox = useRef<HTMLInputElement>(null);
    const ready = useReady();
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            const el = document.activeElement as HTMLElement | null;
            if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey || (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.isContentEditable))) return;
            e.preventDefault();
            findBox.current?.focus();
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, []);
    const q = useQuery({ queryKey: ["course", course], queryFn: () => api.course(course) });
    const c: CourseOverview | undefined = q.data;
    const allModules = c?.projects.flatMap((p) => p.modules) ?? [];
    const modules = allModules.length;
    const current = allModules.flatMap((m) => m.stages).find((s) => s.id === c?.current);
    const here = allModules.find((m) => m.stages.some((s) => s.id === c?.current));
    const hereDone = here?.stages.filter((s) => s.state !== "todo").length ?? 0;
    const needle = find.trim().toLowerCase();
    // Searching or filtering shows every module that has a match, open; the module toggles rest meanwhile.
    const active = filter !== "all" || needle !== "";
    const matches = (x: CourseStageRow, m: { code: string; title: string }) => {
        const okFilter = filter === "all" || (filter === "boss" ? x.kind === "boss" : filter === "done" ? x.state !== "todo" : x.state === "todo");
        const okText = !needle || `${x.title} ${x.id} ${m.title} ${m.code}`.toLowerCase().includes(needle);
        return okFilter && okText;
    };
    const openSet = new Set(openCodes ?? (here ? [here.code] : []));
    const allOpen = allModules.length > 0 && allModules.every((m) => openSet.has(m.code));
    const choose = (codes: string[]) => {
        setOpenCodes(codes);
        setPref("course.open", codes);
    };
    const toggle = (code: string) => choose(openSet.has(code) ? [...openSet].filter((x) => x !== code) : [...openSet, code]);
    const jump = (code: string) => {
        if (!openSet.has(code)) choose([...openSet, code]);
        setFilter("all");
        setFind("");
        requestAnimationFrame(() => document.getElementById(`mod-${code}`)?.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" }));
    };
    const pct = (done: number, total: number) => (total ? Math.round((100 * done) / total) : 0);

    return (
        <>
            <Header area="courses" />
            <MockRoot>
                <div className="k-wrap">
                    <section className="k-hero">
                        <div>
                            <div className="k-eye k-rv" style={{ "--i": 0 } as CSSProperties}>
                                <b>COURSES</b> / CMU 15-445 · BUSTUB
                            </div>
                            <h1 className="k-rv" style={{ "--i": 1 } as CSSProperties}>
                                {c ? <MockTitle title={c.title} /> : "Build a DBMS."}
                            </h1>
                            <p className="k-lead k-rv" style={{ "--i": 2 } as CSSProperties}>
                                BusTub's projects, module by module, in Rust. Every stage is a real piece of the system with tests that mirror BusTub's own, and the last stage of each module is BusTub's own test file, ported.
                            </p>
                        </div>
                        <div className="k-stats k-rv" style={{ "--i": 3 } as CSSProperties}>
                            <div>
                                <b>{c ? <CountUp value={c.total} /> : "–"}</b>
                                <span>STAGES</span>
                            </div>
                            <div>
                                <b>{c ? <CountUp value={c.done} /> : "–"}</b>
                                <span>PASSED</span>
                            </div>
                            <div>
                                <b>{c ? <CountUp value={modules} /> : "–"}</b>
                                <span>MODULES</span>
                            </div>
                        </div>
                    </section>
                    {q.isError && <p className="notice bad">Couldn't load the course: {(q.error as Error).message}</p>}
                    {c && (
                        <div className="k-cmain">
                            <div>
                                {current && here && (
                                    <article className="k-cont k-rv" style={{ "--i": 4 } as CSSProperties}>
                                        <div className="k-k">
                                            <span className="k-pulse" />
                                            {c.done ? "CONTINUE" : "START HERE"} · STAGE {current.rank} OF {c.total}
                                        </div>
                                        <div className="k-ring" aria-label={`${hereDone} of ${here.stages.length} stages in this module passed`}>
                                            <svg viewBox="0 0 64 64">
                                                <circle className="k-t" cx="32" cy="32" r="28" />
                                                <circle className="k-v" cx="32" cy="32" r="28" style={{ strokeDashoffset: ready ? 176 * (1 - hereDone / here.stages.length) : 176 }} />
                                            </svg>
                                            <span>
                                                {hereDone}/{here.stages.length}
                                            </span>
                                        </div>
                                        <div className="k-grow">
                                            <h3>{current.title}</h3>
                                            <small>
                                                {here.code.toUpperCase()} · {here.title} · {EST[current.difficulty]}
                                            </small>
                                        </div>
                                        <Link className="k-cta k-lg" to="/courses/$course/$stage" params={{ course: c.id, stage: current.id }}>
                                            {c.done ? "Resume stage" : "Start here"} <span className="k-ar">→</span>
                                        </Link>
                                    </article>
                                )}

                                <div className="k-map k-rv" style={{ "--i": 5 } as CSSProperties} aria-label="Course map">
                                    <h5>
                                        <span>COURSE MAP</span>
                                        <span>hover a module · click to jump</span>
                                    </h5>
                                    <div>
                                        {c.projects
                                            .filter((p) => p.modules.length > 0)
                                            .map((p) => (
                                                <div className="k-proj" key={p.number}>
                                                    <span>Project {p.number}</span>
                                                    <div className="k-nodes">
                                                        {p.modules.map((m) => {
                                                            const done = m.stages.filter((x) => x.state !== "todo").length;
                                                            return (
                                                                <button key={m.code} className={`k-node${done === m.stages.length ? " k-done" : ""}${m.code === here?.code ? " k-cur" : ""}`} onClick={() => jump(m.code)} aria-label={`${m.code.toUpperCase()} ${m.title}: ${done} of ${m.stages.length} passed`}>
                                                                    {m.code.toUpperCase()}
                                                                    <span className="k-tip" aria-hidden="true">
                                                                        {m.title} · {done}/{m.stages.length}
                                                                    </span>
                                                                </button>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            ))}
                                    </div>
                                </div>

                                <div className="k-tools k-rv" style={{ "--i": 6 } as CSSProperties}>
                                    <label className="k-search">
                                        <span aria-hidden="true">⌕</span>
                                        <input ref={findBox} value={find} onChange={(e) => setFind(e.target.value)} placeholder="find a stage…" autoComplete="off" spellCheck={false} aria-label="Find a stage" onKeyDown={(e) => e.key === "Escape" && e.currentTarget.blur()} />
                                        <kbd>/</kbd>
                                    </label>
                                    <div className="k-seg" role="group" aria-label="Show">
                                        <span className="k-thumb" aria-hidden="true" style={{ width: "calc((100% - 6px) / 4)", transform: `translateX(${FILTERS.findIndex(([k]) => k === filter) * 100}%)` }} />
                                        {FILTERS.map(([k, label]) => (
                                            <button key={k} aria-pressed={filter === k} className={filter === k ? "k-on" : ""} onClick={() => setFilter(k)}>
                                                {label}
                                            </button>
                                        ))}
                                    </div>
                                    <button className="k-ea" onClick={() => choose(allOpen ? [] : allModules.map((m) => m.code))} disabled={active}>
                                        {allOpen ? "COLLAPSE ALL" : "EXPAND ALL"}
                                    </button>
                                </div>
                                {active && !allModules.some((m) => m.stages.some((x) => matches(x, m))) && (
                                    <div className="k-none" role="status">
                                        No stage matches that. <button onClick={() => (setFind(""), setFilter("all"))}>Clear it</button>
                                    </div>
                                )}
                                <div>
                                    {c.projects
                                        .filter((p) => p.modules.length > 0)
                                        .flatMap((p) => p.modules)
                                        .filter((m) => !active || m.stages.some((x) => matches(x, m)))
                                        .map((m) => {
                                            const done = m.stages.filter((x) => x.state !== "todo").length;
                                            const isOpen = active || openSet.has(m.code);
                                            const rows = active ? m.stages.filter((x) => matches(x, m)) : m.stages;
                                            return (
                                                <section className={`k-mod${isOpen ? " k-open" : ""}${m.code === here?.code ? " k-cur" : ""}`} id={`mod-${m.code}`} key={m.code}>
                                                    <button className="k-mh" aria-expanded={isOpen} onClick={() => toggle(m.code)} disabled={active}>
                                                        <span className="k-chev" aria-hidden="true">›</span>
                                                        <span>
                                                            <b>
                                                                {m.code.toUpperCase()} · {m.title}
                                                            </b>
                                                            {m.summary && <p>{m.summary}</p>}
                                                        </span>
                                                        <span className="k-mp">
                                                            <span className="k-mini" aria-hidden="true">
                                                                <i style={{ width: ready ? `${pct(done, m.stages.length)}%` : 0 }} />
                                                            </span>
                                                            {done} / {m.stages.length}
                                                        </span>
                                                    </button>
                                                    <div className="k-body">
                                                        <div inert={!isOpen}>
                                                            <div className="k-rows">
                                                                {rows.map((x, i) => (
                                                                    <StageRow key={x.id} course={c.id} s={x} current={x.id === c.current} index={i} />
                                                                ))}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </section>
                                            );
                                        })}
                                    {c.projects.some((p) => p.modules.length === 0) && (
                                        <>
                                            <div className="k-flabel">PLANNED</div>
                                            <div className="k-mod k-open">
                                                <div className="k-rows">
                                                    {c.projects
                                                        .filter((p) => p.modules.length === 0)
                                                        .map((p) => (
                                                            <div className="k-row" key={p.number} aria-disabled="true" style={{ opacity: 0.65 }}>
                                                                <span className="k-ck" />
                                                                <span className="k-no">P{p.number}</span>
                                                                <span>{p.title}</span>
                                                                <span className="k-next" style={{ color: "var(--dim)" }}>PLANNED</span>
                                                                <span />
                                                            </div>
                                                        ))}
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>
                            <aside className="k-side">
                                <div className="k-sc k-rv" style={{ "--i": 6 } as CSSProperties}>
                                    <h5>
                                        <span>GET STARTED</span>
                                        <span>4 steps</span>
                                    </h5>
                                    {[`anneal course init ${c.id}`, `cd ${c.id}-rs`, `anneal course login ${location.origin}`, "anneal course test"].map((cmd, i) => (
                                        <div className="k-cmd" key={cmd}>
                                            <span className="k-n">{i + 1}</span>
                                            <span>{cmd}</span>
                                            <MockCopy text={cmd} />
                                        </div>
                                    ))}
                                </div>
                                <div className="k-sc k-rv" style={{ "--i": 7 } as CSSProperties}>
                                    <h5>
                                        <span>PROGRESS</span>
                                        <span>
                                            {c.done} / {c.total}
                                        </span>
                                    </h5>
                                    <div>
                                        {c.projects.map((p, i) => {
                                            const st = p.modules.flatMap((m) => m.stages);
                                            const done = st.filter((x) => x.state !== "todo").length;
                                            const v = st.length ? pct(done, st.length) : null;
                                            const first = p.modules[0];
                                            return (
                                                <div key={p.number} className={`k-pr${i === 0 ? " k-act" : ""}`} role="button" tabIndex={first ? 0 : -1} onClick={() => first && jump(first.code)} onKeyDown={(e) => first && (e.key === "Enter" || e.key === " ") && (e.preventDefault(), jump(first.code))}>
                                                    <div className="k-l">
                                                        <span>
                                                            Project {p.number} · {p.title}
                                                        </span>
                                                        <b>{v === null ? "—" : `${v}%`}</b>
                                                    </div>
                                                    <div className="k-mini">
                                                        <i style={{ width: ready ? `${v ?? 0}%` : 0 }} />
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </aside>
                        </div>
                    )}
                </div>
            </MockRoot>
        </>
    );
}

/** "Build a DBMS: BusTub in Rust." with what follows the colon in the course colour and gradient. */
function MockTitle({ title }: { title: string }) {
    const i = title.indexOf(": ");
    if (i < 0) return <>{title}</>;
    return (
        <>
            {title.slice(0, i + 1)} <em>{title.slice(i + 2)}.</em>
        </>
    );
}
