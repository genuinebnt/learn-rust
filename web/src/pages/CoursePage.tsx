import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import type { CSSProperties } from "react";
import { api, type CourseModuleRow, type CourseOverview, type StageDifficulty } from "../api";
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

function ModuleCard({ course, project, m, current }: { course: string; project: number; m: CourseModuleRow; current: string | null }) {
    const done = m.stages.filter((s) => s.state !== "todo").length;
    const next = m.stages.find((s) => s.state === "todo");
    const isCurrent = m.stages.some((s) => s.id === current);
    const finished = done === m.stages.length && m.stages.length > 0;
    const target = next ?? m.stages[0];
    if (!target) return null;
    return (
        <Link className={`tcard ${isCurrent ? "cur" : ""}`} to="/courses/$course/$stage" params={{ course, stage: target.id }}>
            <div className="tc-top">
                <span className="tc-num">{m.code}</span>
                <span className="tc-kind">MODULE / PROJECT {project}</span>
                {isCurrent && <span className="tc-badge" style={{ background: "var(--grn-bg)", color: "var(--grn)" }}>NOW ON</span>}
                {finished && <span className="tc-badge" style={{ background: "var(--grn-bg)", color: "var(--grn)" }}>DONE</span>}
            </div>
            <h3>{m.title}</h3>
            <p>{m.summary}</p>
            <div className="tc-meta">
                <b>{m.stages.length}</b> stages · {m.stages.filter((s) => s.kind === "boss").length} BusTub test{m.stages.filter((s) => s.kind === "boss").length === 1 ? "" : "s"}
            </div>
            <div className="tc-tags">
                {m.stages.slice(0, 3).map((s) => (
                    <span className="cpill" key={s.id}>
                        {s.title}
                    </span>
                ))}
            </div>
            <div className="tc-prog">
                <span>progress</span>
                <span>
                    <b>
                        {done} / {m.stages.length}
                    </b>
                </span>
            </div>
            <div className="tc-bar">
                {m.stages.map((s) => (
                    <span key={s.id} style={{ flex: 1 }}>
                        <i style={{ width: s.state === "todo" ? 0 : "100%", background: DIFFICULTY_COLOR[s.difficulty] }} />
                    </span>
                ))}
            </div>
            <div className="tc-foot">
                <span>{finished ? "all stages passed" : `${done ? "resume" : "start"} · ${next?.title ?? ""}`}</span>
                <span className="tc-go">{finished ? "review ›" : done ? "resume ›" : "start ›"}</span>
            </div>
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
                        <div className="cat-main" style={{ paddingTop: 32 }}>
                            {current && (
                                <Link className="cx-cont" to="/courses/$course/$stage" params={{ course: c.id, stage: current.id }}>
                                    <span className="cx-contk">{c.done ? "CONTINUE" : "START HERE"} · STAGE {current.rank} OF {c.total}</span>
                                    <b>{current.title}</b>
                                    <span className="tc-go">open stage ›</span>
                                </Link>
                            )}
                            {c.projects.filter((p) => p.modules.length > 0).map((p) => {
                                const stages = p.modules.flatMap((m) => m.stages);
                                const done = stages.filter((s) => s.state !== "todo").length;
                                return (
                                    <div key={p.number} style={{ display: "contents" }}>
                                        <div className="flabel">
                                            PROJECT {p.number} · {p.title.toUpperCase()}
                                            {stages.length ? ` · ${done} / ${stages.length}` : ""}
                                        </div>
                                        <div className="tgrid">
                                            {p.modules.map((m) => (
                                                <ModuleCard key={m.code} course={c.id} project={p.number} m={m} current={c.current} />
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                            {c.projects.some((p) => p.modules.length === 0) && (
                                <div style={{ display: "contents" }}>
                                    <div className="flabel">PLANNED</div>
                                    <div className="tlist">
                                        {c.projects
                                            .filter((p) => p.modules.length === 0)
                                            .map((p) => (
                                                <div className="trow" key={p.number} aria-disabled="true" style={{ opacity: 0.7 }}>
                                                    <span className="n">{p.number}</span>
                                                    <span className="t">
                                                        {p.title}
                                                        <small>PROJECT {p.number} · NOT WRITTEN YET</small>
                                                    </span>
                                                    <span className="x hide" />
                                                    <span className="hide" />
                                                    <span className="x">planned</span>
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}
