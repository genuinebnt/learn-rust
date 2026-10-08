import { Link, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fragment, useEffect, useState } from "react";
import { api, type CourseStagePage as Page, type CourseStageRow, type SolutionFile } from "../api";
import { Header } from "../components/Header";
import { DIFFICULTY_COLOR, SplitTitle } from "./CoursePage";
import { renderMd } from "./courseMd";

const md = renderMd;
const DIFFICULTY_LABEL = { "very-easy": "VERY EASY", easy: "EASY", medium: "MEDIUM", hard: "HARD" } as const;

/** Copies a code block when its copy button is clicked (the HTML is static, so the click is caught here). */
function copyFromBlock(e: React.MouseEvent) {
    const b = (e.target as HTMLElement).closest<HTMLButtonElement>(".cx-copy");
    if (!b) return;
    const done = () => {
        b.textContent = "copied";
        setTimeout(() => (b.textContent = "copy"), 1200);
    };
    try {
        navigator.clipboard.writeText(b.dataset.code ?? "").then(done, done);
    } catch {
        done();
    }
}

function Prose({ text }: { text: string }) {
    return <div onClick={copyFromBlock} dangerouslySetInnerHTML={{ __html: md(text) }} />;
}

/** Splits markdown at its `### ` headings (not inside code fences): [title | null, body]. */
function blocks(text: string): [string | null, string][] {
    const out: [string | null, string][] = [[null, ""]];
    const add = (line: string) => {
        const last = out[out.length - 1];
        if (last) last[1] += line + "\n";
    };
    let fence = false;
    for (const line of text.split("\n")) {
        if (line.trimStart().startsWith("```")) fence = !fence;
        if (!fence && line.startsWith("### ")) {
            out.push([line.slice(4).trim(), ""]);
            continue;
        }
        add(line);
    }
    return out.filter(([t, b]) => t !== null || b.trim());
}

/** A stage part or section: prose, with "The task" lifted into the highlighted Your turn box. */
function Body({ text }: { text: string }) {
    return (
        <>
            {blocks(text).map(([title, body], i) =>
                title === "The task" ? (
                    <section className="cx-task" key={i}>
                        <div className="cx-th">
                            <b>YOUR TURN</b>
                            <span>
                                run <kbd>anneal course test</kbd> or push
                            </span>
                        </div>
                        <div className="cx-tb cx-prose">
                            <Prose text={body} />
                        </div>
                    </section>
                ) : (
                    <Fragment key={i}>
                        {title && <h3>{title}</h3>}
                        <Prose text={body} />
                    </Fragment>
                ),
            )}
        </>
    );
}

function DiffView({ files }: { files: SolutionFile[] }) {
    return (
        <>
            {files.map((f) => (
                <figure className="cx-diff" key={f.path}>
                    <pre>
                        {f.lines.map((l, i) => (
                            <span key={i} className={`cx-ln${l.startsWith("+") ? " add" : l.startsWith("-") ? " del" : ""}`}>
                                {l || " "}
                            </span>
                        ))}
                    </pre>
                    <figcaption>{f.path}</figcaption>
                </figure>
            ))}
        </>
    );
}

function ago(iso: string) {
    const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (s < 60) return "just now";
    if (s < 3600) return `${Math.floor(s / 60)} min ago`;
    if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
    return `${Math.floor(s / 86400)} d ago`;
}

function Sidebar({ course, page }: { course: string; page: Page }) {
    const overview = useQuery({ queryKey: ["course", course], queryFn: () => api.course(course) });
    const o = overview.data;
    return (
        <aside className="cx-side">
            <div className="cx-sh">
                <small>COURSE</small>
                <b>{page.course.title}</b>
                {o && (
                    <>
                        <div className="cx-prog">
                            {o.projects
                                .flatMap((p) => p.modules)
                                .flatMap((m) => m.stages)
                                .map((s) => (
                                    <i key={s.id} className={s.state !== "todo" ? "d" : ""} />
                                ))}
                        </div>
                        <div className="cx-pl">
                            {o.done} of {o.total} stages passed
                        </div>
                    </>
                )}
            </div>
            <nav className="cx-tree" aria-label="Course">
                {o?.projects.map((p) => (
                    <Fragment key={p.number}>
                        <Link className={`cx-node${p.modules.length ? "" : " dim"}`} to="/courses/$course" params={{ course }}>
                            <span className="cx-nt">
                                Project {p.number} · {p.title}
                            </span>
                            <span className="cx-nc">{p.modules.length ? `${p.modules.flatMap((m) => m.stages).filter((s) => s.state !== "todo").length}/${p.modules.flatMap((m) => m.stages).length}` : "planned"}</span>
                        </Link>
                        {p.modules.length > 0 && (
                            <div className="cx-kids">
                                {p.modules.map((m) => {
                                    const here = m.code === page.module.code;
                                    const open = here;
                                    return (
                                        <Fragment key={m.code}>
                                            <Link className="cx-node" to="/courses/$course/$stage" params={{ course, stage: (m.stages.find((s) => s.state === "todo") ?? m.stages[0])?.id ?? "" }}>
                                                <span className="cx-car">{open ? "▾" : "▸"}</span>
                                                <span className="cx-nt">
                                                    {m.code} · {m.title}
                                                </span>
                                                <span className="cx-nc">
                                                    {m.stages.filter((s) => s.state !== "todo").length}/{m.stages.length}
                                                </span>
                                            </Link>
                                            {open && (
                                                <div className="cx-leaves">
                                                    {m.stages.map((s: CourseStageRow, i) => (
                                                        <Link key={s.id} className={`cx-leaf${s.id === page.stage.id ? " cur" : ""}${s.kind === "boss" ? " boss" : ""}`} to="/courses/$course/$stage" params={{ course, stage: s.id }}>
                                                            <span className={`cx-si${s.state !== "todo" ? " ok" : s.id === page.stage.id ? " now" : ""}`}>{s.state !== "todo" ? "✓" : ""}</span>
                                                            <span className="cx-ln2">{String(i + 1).padStart(2, "0")}</span>
                                                            <span className="cx-lt">{s.title}</span>
                                                            <span className="cx-dot" style={{ background: DIFFICULTY_COLOR[s.difficulty] }} title={s.difficulty} />
                                                        </Link>
                                                    ))}
                                                </div>
                                            )}
                                        </Fragment>
                                    );
                                })}
                            </div>
                        )}
                    </Fragment>
                ))}
            </nav>
        </aside>
    );
}

export function CourseStagePage({ course, stage }: { course: string; stage: string }) {
    const qc = useQueryClient();
    const nav = useNavigate();
    const key = ["course-stage", course, stage];
    const q = useQuery({ queryKey: key, queryFn: () => api.courseStage(course, stage) });
    const set = (p: Page) => {
        qc.setQueryData(key, p);
        qc.invalidateQueries({ queryKey: ["course", course] });
    };
    const hint = useMutation({ mutationFn: () => api.revealCourseHint(course, stage), onSuccess: set });
    const sol = useMutation({ mutationFn: () => api.revealCourseSolution(course, stage), onSuccess: set });
    const p = q.data;
    const [active, setActive] = useState("s-top");

    useEffect(() => {
        window.scrollTo({ top: 0 });
    }, [stage]);
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            if (e.metaKey || e.ctrlKey || e.altKey || (e.target as HTMLElement | null)?.closest("input, textarea, [contenteditable]")) return;
            const to = e.key === "[" ? p?.prev : e.key === "]" ? p?.next : null;
            if (to) nav({ to: "/courses/$course/$stage", params: { course, stage: to.id } });
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [p, course, nav]);
    const ids = p ? ["s-top", ...p.stage.sections.map((s) => `sec-${s.id}`), "s-hints", "s-solution", "s-run", "s-deeper"] : [];
    useEffect(() => {
        const onScroll = () => {
            let cur = ids[0] ?? "s-top";
            for (const id of ids) {
                const el = document.getElementById(id);
                if (el && el.getBoundingClientRect().top < 200) cur = id;
            }
            setActive(cur);
        };
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
        return () => window.removeEventListener("scroll", onScroll);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [p?.stage.id]);

    if (q.isError) {
        return (
            <>
                <Header area="courses" />
                <main className="page">
                    <div className="wrap">
                        <p className="notice bad">Couldn't load {stage}: {(q.error as Error).message}</p>
                    </div>
                </main>
            </>
        );
    }
    if (!p) {
        return (
            <>
                <Header area="courses" />
                <main className="page">
                    <div className="wrap">
                        <p className="notice">Loading…</p>
                    </div>
                </main>
            </>
        );
    }
    const inModule = p.module.stages.findIndex((s) => s.id === p.stage.id);
    const run = p.last_run;
    const nextHint = p.hints.revealed.length < p.hints.total ? p.hints.titles[p.hints.revealed.length] : null;
    const toc: [string, string][] = [
        ["s-top", "Overview"],
        ...p.stage.sections.map((s): [string, string] => [`sec-${s.id}`, s.title]),
        ...(p.concepts.length ? ([["s-concepts", "Concepts"]] as [string, string][]) : []),
        ...(p.hints.total ? ([["s-hints", "Hints"]] as [string, string][]) : []),
        ["s-solution", "Our answer"],
        ["s-run", "Your last run"],
        ["s-deeper", "Go deeper"],
    ];
    return (
        <>
            <Header area="courses" />
            <div className="subbar cx-sub">
                <div className="crumb">
                    <Link to="/courses" style={{ color: "var(--grn)" }}>
                        COURSES
                    </Link>
                    <span>/</span>
                    <span>PROJECT {p.module.project}</span>
                    <span>/</span>
                    <span>
                        {p.module.code.toUpperCase()} {p.module.title.toUpperCase()}
                    </span>
                </div>
                <div className="vr" />
                <span className="wtitle">{p.stage.title}</span>
                <div className="subpills">
                    <span className="pill solid" style={{ background: p.stage.kind === "boss" ? "var(--warn)" : "var(--grn)" }}>
                        {p.stage.kind === "boss" ? "BOSS" : "STAGE"}
                    </span>
                    <span className="pill" style={{ borderColor: DIFFICULTY_COLOR[p.stage.difficulty], color: DIFFICULTY_COLOR[p.stage.difficulty] }}>
                        {DIFFICULTY_LABEL[p.stage.difficulty]}
                    </span>
                    {p.state !== "todo" && <span className="pill">{p.state === "assisted" ? "PASSED · ASSISTED" : "PASSED"}</span>}
                </div>
                <div className="sbr">
                    <span className="cx-nav">
                        {p.prev ? (
                            <Link to="/courses/$course/$stage" params={{ course, stage: p.prev.id }} aria-label="Previous stage">
                                ‹
                            </Link>
                        ) : (
                            <span style={{ color: "var(--line)" }}>‹</span>
                        )}
                        <span>
                            {p.stage.rank} / {p.course.total}
                        </span>
                        {p.next ? (
                            <Link to="/courses/$course/$stage" params={{ course, stage: p.next.id }} aria-label="Next stage">
                                ›
                            </Link>
                        ) : (
                            <span style={{ color: "var(--line)" }}>›</span>
                        )}
                    </span>
                </div>
            </div>
            <div className="cx" style={{ "--ca": "var(--grn)", "--cab": "var(--grn-bg)" } as React.CSSProperties}>
                <Sidebar course={course} page={p} />
                <div className="cx-main">
                    <main className="cx-read">
                        <div className="cx-col">
                            <div className="eyebrow" id="s-top">
                                <span style={{ color: "var(--grn)" }}>
                                    {p.module.code.toUpperCase()} · STAGE {inModule + 1} OF {p.module.stages.length}
                                </span>
                                <span>/</span>
                                <span>{DIFFICULTY_LABEL[p.stage.difficulty]}</span>
                                <span>/</span>
                                <span>#{p.stage.id}</span>
                            </div>
                            <h1 className="cx-h1">
                                <SplitTitle title={p.stage.title} />
                            </h1>
                            {p.stage.intro && (
                                <div className="cx-lead cx-leadmd">
                                    <Prose text={p.stage.intro} />
                                </div>
                            )}
                            {p.concepts.length > 0 && (
                                <div className="cx-prose">
                                    <div className="cx-part" id="s-concepts">
                                        <b>READ FIRST</b>
                                        CONCEPTS FOR THIS STAGE
                                    </div>
                                    <div className="cx-reads">
                                        {p.concepts.map((k) => (
                                            <Link key={k.id} to="/courses/$course/concept/$id" params={{ course, id: k.id }} className="cx-concept">
                                                <small>CONCEPT · ~{k.minutes} MIN</small>
                                                {k.title}
                                                <span>{k.summary}</span>
                                            </Link>
                                        ))}
                                    </div>
                                </div>
                            )}
                            <div className="cx-prose">
                                {p.stage.sections.map((s, i) => {
                                    const part = /^Part (\d+) · (.*)$/.exec(s.title);
                                    return (
                                        <section key={s.id} id={`sec-${s.id}`}>
                                            <div className="cx-part">
                                                <b>{part ? `PART ${part[1]}` : String(i + 1).padStart(2, "0")}</b>
                                                {part ? "" : s.title.toUpperCase()}
                                            </div>
                                            {part && <h2>{part[2]}</h2>}
                                            <Body text={s.md} />
                                        </section>
                                    );
                                })}

                                {p.hints.total > 0 && (
                                    <section id="s-hints">
                                        <div className="cx-part">
                                            <b>HINTS</b>
                                            {p.hints.revealed.length} OF {p.hints.total} OPENED
                                        </div>
                                        <p className="cx-quiet" style={{ margin: "14px 0 0" }}>
                                            Each hint opened before the stage passes marks it as assisted. They get deeper: the first nudges the design, the last names the invariant to check.
                                        </p>
                                        {p.hints.revealed.map((h, i) => (
                                            <details className="cx-box vio" key={i} open>
                                                <summary>
                                                    <span className="cx-bl">Hint {i + 1}</span>
                                                    <span className="cx-bt">{h.title}</span>
                                                    <span className="cx-chev" aria-hidden="true" />
                                                </summary>
                                                <div className="cx-bb">
                                                    <Prose text={h.md} />
                                                </div>
                                            </details>
                                        ))}
                                        {nextHint !== null && (
                                            <div className="cx-locked vio">
                                                <b>HINT {p.hints.revealed.length + 1}</b>
                                                <span>{p.state === "todo" ? "Opening it marks this stage as assisted." : "Locked until you open it."}</span>
                                                <button onClick={() => hint.mutate()} disabled={hint.isPending}>
                                                    open hint {p.hints.revealed.length + 1} of {p.hints.total}
                                                </button>
                                            </div>
                                        )}
                                    </section>
                                )}

                                {(
                                    <section id="s-solution">
                                        <div className="cx-part">
                                            <b>OUR ANSWER</b>
                                            {p.solution.open ? "OPENED" : "LOCKED"}
                                        </div>
                                        {p.solution.open && p.solution.files ? (
                                            <>
                                                <p className="cx-quiet" style={{ margin: "14px 0 0" }}>
                                                    One way to write it, as a diff against your starter code. Yours only has to pass the tests.
                                                </p>
                                                <DiffView files={p.solution.files} />
                                            </>
                                        ) : !p.solution.available ? (
                                            <div className="cx-locked fn">
                                                <b>OUR ANSWER</b>
                                                <span>
                                                    Not uploaded to this app yet. From your clone of the repo: <code>anneal course login {location.origin}</code>, then <code>anneal course solutions</code>.
                                                </span>
                                            </div>
                                        ) : (
                                            <div className="cx-locked fn">
                                                <b>OUR ANSWER</b>
                                                <span>{p.state === "todo" ? "Opening it before the stage passes marks it as assisted." : "Unlocked once the stage has passed."}</span>
                                                <button onClick={() => sol.mutate()} disabled={sol.isPending}>
                                                    show the solution
                                                </button>
                                            </div>
                                        )}
                                    </section>
                                )}

                                <section id="s-run">
                                    <div className="cx-part">
                                        <b>YOUR LAST RUN</b>
                                        {run ? ago(run.at).toUpperCase() : ""}
                                    </div>
                                    {run ? (
                                        <>
                                            {run.problem && (
                                                <div className="cx-test bad" style={{ margin: "14px 0 0", padding: 0 }}>
                                                    <span className="cx-sq" />
                                                    <div>
                                                        <div className="cx-tn">did not run</div>
                                                        <div className="cx-fail">
                                                            <code style={{ whiteSpace: "pre-wrap" }}>{run.problem}</code>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                            <div className="cx-tests">
                                                {run.tests.map((t) => (
                                                    <div className={`cx-test ${t.ok ? "ok" : "bad"}`} key={t.name}>
                                                        <span className="cx-sq" />
                                                        <div>
                                                            <div className="cx-tn">{t.name}</div>
                                                            {!t.ok && t.detail && (
                                                                <div className="cx-fail">
                                                                    <span>failed</span>
                                                                    <code style={{ whiteSpace: "pre-wrap" }}>{t.detail}</code>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </>
                                    ) : (
                                        <div className="cx-empty">
                                            No run yet. In your repo, run <code>anneal course test</code>, or commit and push: each run is reported here.
                                        </div>
                                    )}
                                </section>

                                <section id="s-deeper">
                                    <div className="cx-part">
                                        <b>GO DEEPER</b>
                                        {p.module.code.toUpperCase()} · {p.module.title.toUpperCase()}
                                    </div>
                                    <div className="cx-reads">
                                        {p.module.lectures.map((l) => (
                                            <a key={l.id} href={l.video ?? l.slides} target="_blank" rel="noreferrer">
                                                <small>CMU 15-445 LECTURE · {l.term.toUpperCase()}</small>
                                                {l.title}
                                                <span>
                                                    {[l.slides && "slides", l.notes && "notes", l.video && "video"].filter(Boolean).join(" · ")}
                                                </span>
                                            </a>
                                        ))}
                                        {p.module.resources.map((r) => (
                                            <a key={r.url} href={r.url} target="_blank" rel="noreferrer">
                                                <small>{r.kind.toUpperCase()}</small>
                                                {r.title}
                                            </a>
                                        ))}
                                        {p.module.bustub.map((u) => (
                                            <a key={u} href={u} target="_blank" rel="noreferrer">
                                                <small>BUSTUB SOURCE</small>
                                                {u.split("/").slice(-1)[0]}
                                                <span>{u.replace("https://github.com/cmu-db/bustub/blob/master/", "")}</span>
                                            </a>
                                        ))}
                                    </div>
                                </section>
                            </div>
                            <nav className="cx-pn">
                                {p.prev ? (
                                    <Link to="/courses/$course/$stage" params={{ course, stage: p.prev.id }}>
                                        <small>
                                            ‹ PREVIOUS <kbd>[</kbd>
                                        </small>
                                        {p.prev.title}
                                    </Link>
                                ) : (
                                    <span />
                                )}
                                {p.next ? (
                                    <Link to="/courses/$course/$stage" params={{ course, stage: p.next.id }}>
                                        <small>
                                            NEXT <kbd>]</kbd> ›
                                        </small>
                                        {p.next.title}
                                    </Link>
                                ) : (
                                    <span />
                                )}
                            </nav>
                        </div>
                    </main>
                    <div className="cx-bar">
                        {run ? (
                            <>
                                <span className="d" style={run.ok ? { background: "var(--grn)", boxShadow: "0 0 0 3px var(--grn-bg)" } : undefined} />
                                <b>{run.ok ? "stage passed" : run.problem ? "did not run" : `${run.passed} / ${run.total} passing`}</b>
                                <span className="sq">
                                    {run.tests.map((t) => (
                                        <i key={t.name} className={t.ok ? "g" : ""} />
                                    ))}
                                </span>
                                <span className="cx-ls">
                                    run · {ago(run.at)}
                                    {run.commit_sha ? ` · ${run.commit_sha.slice(0, 7)}` : ""}
                                </span>
                            </>
                        ) : (
                            <>
                                <span className="d" style={{ background: "var(--line)", boxShadow: "none" }} />
                                <b>no run yet</b>
                                <span className="cx-ls">
                                    run <code>anneal course test</code> in your repo
                                </span>
                            </>
                        )}
                    </div>
                </div>
                <aside className="cx-toc">
                    <div>
                        <h4>ON THIS PAGE</h4>
                        {toc.map(([id, label]) => (
                            <a key={id} href={`#${id}`} className={active === id ? "on" : ""} onClick={(e) => { e.preventDefault(); document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" }); }}>
                                {label}
                            </a>
                        ))}
                    </div>
                    <div>
                        <h4>SHORTCUTS</h4>
                        <p>
                            <kbd>[</kbd> <kbd>]</kbd> previous / next stage
                        </p>
                    </div>
                </aside>
            </div>
        </>
    );
}
