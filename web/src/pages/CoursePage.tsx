import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState, type CSSProperties } from "react";
import { api, type CourseOverview, type CourseStageRow, type StageDifficulty } from "../api";
import { Header } from "../components/Header";
import { CopyButton } from "../components/kit";
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

function StageRow({ course, s, current, index }: { course: string; s: CourseStageRow; current: boolean; index: number }) {
    return (
        <Link className={`cx-srow${current ? " cur" : ""}`} style={{ "--k": index } as CSSProperties} to="/courses/$course/$stage" params={{ course, stage: s.id }}>
            <span className={`cx-sdot${s.state === "solved" ? " ok" : s.state === "assisted" ? " asst" : ""}`} aria-label={s.state === "todo" ? "not passed" : "passed"}>
                {s.state === "todo" ? "" : "✓"}
            </span>
            <span className="cx-sno">{s.id.split("-")[1]}</span>
            <span className="cx-stt">
                {s.title}
                {s.kind === "boss" && <em>BUSTUB TEST</em>}
            </span>
            {current && <span className="cx-now">UP NEXT</span>}
            <DifficultyMark d={s.difficulty} />
        </Link>
    );
}

type Filter = "all" | "todo" | "done" | "boss";
const FILTERS: [Filter, string][] = [
    ["all", "all"],
    ["todo", "to do"],
    ["done", "passed"],
    ["boss", "boss"],
];

export function CoursePage({ course = COURSE_ID }: { course?: string }) {
    // Which modules are open: remembered in this browser; until there is a choice, only the module you are in.
    const [openCodes, setOpenCodes] = useState<string[] | null>(() => getPref<string[] | null>("course.open", null));
    const [filter, setFilter] = useState<Filter>("all");
    const [find, setFind] = useState("");
    const findBox = useRef<HTMLInputElement>(null);
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
    const modules = c?.projects.reduce((n, p) => n + p.modules.length, 0) ?? 0;
    const current = c?.projects.flatMap((p) => p.modules).flatMap((m) => m.stages).find((s) => s.id === c.current);
    const here = c?.projects.flatMap((p) => p.modules).find((m) => m.stages.some((s) => s.id === c.current));
    const hereDone = here?.stages.filter((s) => s.state !== "todo").length ?? 0;
    const style = { "--ca": "var(--grn)", "--cab": "var(--grn-bg)" } as CSSProperties;
    const allModules = c?.projects.flatMap((p) => p.modules) ?? [];
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
        requestAnimationFrame(() => document.getElementById(`mod-${code}`)?.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" }));
    };
    return (
        <>
            <Header area="courses" />
            <main className="page" style={style}>
                <div className="wrap">
                    <section className="cat-top">
                        <div style={{ minWidth: 0, flex: "1 1 520px" }}>
                            <div className="eyebrow">
                                <span style={{ color: "var(--ca)" }}>COURSES</span>
                                <span>/</span>
                                <span>CMU 15-445 · BUSTUB</span>
                            </div>
                            <h1 className="h1 md">{c ? <SplitTitle title={c.title} /> : "Build a DBMS."}</h1>
                            <p className="lead">
                                BusTub's projects, module by module, in Rust. Every stage is a real piece of the system with tests that mirror BusTub's own, and the last stage of each module is BusTub's own test file, ported.
                                You work in your own repo with <code>anneal course init</code>, and <code>git push</code> reports each run here.
                            </p>
                        </div>
                        <div className="cat-stats">
                            <div>
                                <b>{c?.total ?? "–"}</b>
                                <span>STAGES</span>
                            </div>
                            <div>
                                <b>{c?.done ?? "–"}</b>
                                <span>PASSED</span>
                            </div>
                            <div>
                                <b>{c ? modules : "–"}</b>
                                <span>MODULES</span>
                            </div>
                        </div>
                    </section>
                    {q.isError && <p className="notice bad">Couldn't load the course: {(q.error as Error).message}</p>}
                    {c && (
                      <div className="cat-body">
                        <div className="cat-main">
                            {current && (
                                <Link className="cx-cont" to="/courses/$course/$stage" params={{ course: c.id, stage: current.id }}>
                                    <span className="cx-contk">{c.done ? "CONTINUE" : "START HERE"} · STAGE {current.rank} OF {c.total}</span>
                                    {here && (
                                        <span className="cx-ring" style={{ "--p": Math.round((100 * hereDone) / here.stages.length) } as React.CSSProperties} aria-label={`${hereDone} of ${here.stages.length} stages in this module passed`}>
                                            <span>
                                                {hereDone}/{here.stages.length}
                                            </span>
                                        </span>
                                    )}
                                    <span className="cx-contb">
                                        <b>{current.title}</b>
                                        {here && (
                                            <small>
                                                {here.code.toUpperCase()} · {here.title}
                                            </small>
                                        )}
                                    </span>
                                    <span className="tc-go">open stage ›</span>
                                </Link>
                            )}
                            <div className="cx-map" aria-label="Course map">
                                <h4>
                                    <span>COURSE MAP</span>
                                    <span>hover a module · click to open it</span>
                                </h4>
                                {c.projects
                                    .filter((p) => p.modules.length > 0)
                                    .map((p) => (
                                        <div className="cx-mp" key={p.number}>
                                            <span>Project {p.number}</span>
                                            <div className="cx-nodes">
                                                {p.modules.map((m) => {
                                                    const done = m.stages.filter((x) => x.state !== "todo").length;
                                                    return (
                                                        <button
                                                            key={m.code}
                                                            className={`cx-node${done === m.stages.length ? " done" : ""}${m.code === here?.code ? " cur" : ""}`}
                                                            onClick={() => jump(m.code)}
                                                            aria-label={`${m.code.toUpperCase()} ${m.title}: ${done} of ${m.stages.length} passed`}
                                                        >
                                                            {m.code.toUpperCase()}
                                                            <span className="cx-tip" aria-hidden="true">
                                                                {m.title} · {done}/{m.stages.length}
                                                            </span>
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    ))}
                            </div>
                            <div className="cx-tools">
                                <label className="cx-find">
                                    <span aria-hidden="true">⌕</span>
                                    <input ref={findBox} value={find} onChange={(e) => setFind(e.target.value)} placeholder="find a stage…" autoComplete="off" spellCheck={false} aria-label="Find a stage" onKeyDown={(e) => e.key === "Escape" && e.currentTarget.blur()} />
                                    <kbd>/</kbd>
                                </label>
                                <div className="cx-seg" role="group" aria-label="Show" style={{ "--i": FILTERS.findIndex(([k]) => k === filter) } as CSSProperties}>
                                    <span className="cx-thumb" aria-hidden="true" />
                                    {FILTERS.map(([k, label]) => (
                                        <button key={k} aria-pressed={filter === k} className={filter === k ? "on" : ""} onClick={() => setFilter(k)}>
                                            {label}
                                        </button>
                                    ))}
                                </div>
                                <button className="cx-ea" onClick={() => choose(allOpen ? [] : allModules.map((m) => m.code))} disabled={active}>
                                    {allOpen ? "COLLAPSE ALL" : "EXPAND ALL"}
                                </button>
                            </div>
                            {active && !c.projects.some((p) => p.modules.some((m) => m.stages.some((x) => matches(x, m)))) && (
                                <div className="cx-none" role="status">
                                    No stage matches that. <button onClick={() => (setFind(""), setFilter("all"))}>Clear it</button>
                                </div>
                            )}
                            {c.projects
                                .filter((p) => p.modules.length > 0)
                                .map((p) => {
                                    const shown = p.modules.filter((m) => !active || m.stages.some((x) => matches(x, m)));
                                    if (shown.length === 0) return null;
                                    return (
                                        <div key={p.number} style={{ display: "contents" }}>
                                            <div className="flabel">PROJECT {p.number} · {p.title.toUpperCase()}</div>
                                            {shown.map((m) => {
                                                const done = m.stages.filter((x) => x.state !== "todo").length;
                                                const isOpen = active || openSet.has(m.code);
                                                const rows = active ? m.stages.filter((x) => matches(x, m)) : m.stages;
                                                return (
                                                    <section className={`cx-mod${isOpen ? " open" : ""}${m.code === here?.code ? " cur" : ""}`} id={`mod-${m.code}`} key={m.code}>
                                                        <button className="cx-mh" aria-expanded={isOpen} onClick={() => toggle(m.code)} disabled={active}>
                                                            <span className="cx-chev" aria-hidden="true">›</span>
                                                            <span className="cx-mt">
                                                                <b>
                                                                    {m.code.toUpperCase()} · {m.title}
                                                                </b>
                                                                {m.summary && <span className="cx-msum">{m.summary}</span>}
                                                            </span>
                                                            <span className="cx-mc">
                                                                <span className="cx-mini" aria-hidden="true">
                                                                    <i style={{ width: `${Math.round((100 * done) / m.stages.length)}%` }} />
                                                                </span>
                                                                {done} / {m.stages.length}
                                                            </span>
                                                        </button>
                                                        <div className="cx-mb">
                                                            <div inert={!isOpen}>
                                                                <div className="cx-srows">
                                                                    {rows.map((x, i) => (
                                                                        <StageRow key={x.id} course={c.id} s={x} current={x.id === c.current} index={i} />
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </section>
                                                );
                                            })}
                                        </div>
                                    );
                                })}
                            {c.projects.some((p) => p.modules.length === 0) && (
                                <div style={{ display: "contents" }}>
                                    <div className="flabel">PLANNED</div>
                                    <div className="cx-srows">
                                        {c.projects
                                            .filter((p) => p.modules.length === 0)
                                            .map((p) => (
                                                <div className="cx-srow plan" key={p.number} aria-disabled="true">
                                                    <span className="cx-sdot" />
                                                    <span className="cx-sno">P{p.number}</span>
                                                    <span className="cx-stt">{p.title}</span>
                                                    <span className="cx-now dim">PLANNED</span>
                                                    <span />
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            )}
                        </div>
                        <aside className="cat-rail" aria-label="Course">
                            <div className="rbox">
                                <h4>
                                    <span>GET STARTED</span>
                                </h4>
                                <div className="cx-cmds">
                                    {[`anneal course init ${c.id}`, `cd ${c.id}-rs`, `anneal course login ${location.origin}`, "anneal course test"].map((cmd, i) => (
                                        <div className="cx-cmd" key={cmd}>
                                            <span className="n">{i + 1}</span>
                                            <code>{cmd}</code>
                                            <CopyButton text={cmd} />
                                        </div>
                                    ))}
                                </div>
                                <p className="note" style={{ marginTop: 10 }}>
                                    Edit the stubs in your own repo. <code>git push</code> runs the tests and reports each run here.
                                </p>
                            </div>
                            <div className="rbox">
                                <h4>
                                    <span>PROGRESS</span>
                                    <span style={{ color: "var(--ca)" }}>
                                        {c.done} / {c.total}
                                    </span>
                                </h4>
                                {c.projects.map((p) => {
                                    const st = p.modules.flatMap((m) => m.stages);
                                    const done = st.filter((x) => x.state !== "todo").length;
                                    const pct = st.length ? Math.round((100 * done) / st.length) : null;
                                    return (
                                        <button className="rmeter link" key={p.number} style={{ marginBottom: 6 }} disabled={!p.modules[0]} onClick={() => p.modules[0] && jump(p.modules[0].code)}>
                                            <span>
                                                Project {p.number} · {p.title}
                                            </span>
                                            <em style={{ color: pct === null ? "var(--dim)" : "var(--grn)" }}>{pct === null ? "—" : `${pct}%`}</em>
                                            <i>
                                                <b style={{ width: `${pct ?? 0}%`, background: "var(--grn)" }} />
                                            </i>
                                        </button>
                                    );
                                })}
                            </div>
                        </aside>
                      </div>
                    )}
                </div>
            </main>
        </>
    );
}
