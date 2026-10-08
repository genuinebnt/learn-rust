import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import type { CSSProperties } from "react";
import { api, type CourseOverview, type CourseStageRow, type StageDifficulty } from "../api";
import { Header } from "../components/Header";

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

function StageRow({ course, s, current }: { course: string; s: CourseStageRow; current: boolean }) {
    return (
        <Link className={`cx-srow${current ? " cur" : ""}`} to="/courses/$course/$stage" params={{ course, stage: s.id }}>
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

export function CoursePage({ course = COURSE_ID }: { course?: string }) {
    const q = useQuery({ queryKey: ["course", course], queryFn: () => api.course(course) });
    const c: CourseOverview | undefined = q.data;
    const modules = c?.projects.reduce((n, p) => n + p.modules.length, 0) ?? 0;
    const current = c?.projects.flatMap((p) => p.modules).flatMap((m) => m.stages).find((s) => s.id === c.current);
    const style = { "--ca": "var(--grn)", "--cab": "var(--grn-bg)" } as CSSProperties;
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
                                    <b>{current.title}</b>
                                    <span className="tc-go">open stage ›</span>
                                </Link>
                            )}
                            {c.projects
                                .filter((p) => p.modules.length > 0)
                                .map((p) => (
                                    <div key={p.number} style={{ display: "contents" }}>
                                        <div className="flabel">PROJECT {p.number} · {p.title.toUpperCase()}</div>
                                        {p.modules.map((m) => {
                                            const done = m.stages.filter((x) => x.state !== "todo").length;
                                            return (
                                                <section className="cx-sec" key={m.code}>
                                                    <div className="cx-sech">
                                                        <b>
                                                            {m.code.toUpperCase()} · {m.title}
                                                        </b>
                                                        <span>
                                                            {done} / {m.stages.length} stages
                                                        </span>
                                                    </div>
                                                    {m.summary && <p className="cx-secp">{m.summary}</p>}
                                                    <div className="cx-srows">
                                                        {m.stages.map((x) => (
                                                            <StageRow key={x.id} course={c.id} s={x} current={x.id === c.current} />
                                                        ))}
                                                    </div>
                                                </section>
                                            );
                                        })}
                                    </div>
                                ))}
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
                                    <code>anneal course init {c.id}</code>
                                    <code>cd {c.id}-rs</code>
                                    <code>anneal course login {location.origin}</code>
                                    <code>anneal course test</code>
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
                                        <div className="rmeter" key={p.number} style={{ marginBottom: 6 }}>
                                            <span>
                                                Project {p.number} · {p.title}
                                            </span>
                                            <em style={{ color: pct === null ? "var(--dim)" : "var(--grn)" }}>{pct === null ? "—" : `${pct}%`}</em>
                                            <i>
                                                <b style={{ width: `${pct ?? 0}%`, background: "var(--grn)" }} />
                                            </i>
                                        </div>
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
