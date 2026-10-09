import { Link, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fragment, useEffect, useLayoutEffect, useRef, useState } from "react";
import { api, type CourseRun, type CourseStagePage as Page, type CourseStageRow, type SolutionFile, type StageDifficulty } from "../api";
import { Header } from "../components/Header";
import { DIFFICULTY_COLOR, SplitTitle } from "./CoursePage";
import { handleCodeClick, renderMd } from "./courseMd";
import { Celebration, CopyButton, celebrateOff } from "../components/kit";
import { FocusTimer } from "../components/FocusTimer";
import { Resizer, usePanels, type PanelsApi } from "./stagePanels";
import { getPref, setPref } from "../prefs";

const md = renderMd;
type Tab = "instructions" | "hints" | "solution" | "concepts" | "run";
const DIFFICULTY_LABEL = { "very-easy": "VERY EASY", easy: "EASY", medium: "MEDIUM", hard: "HARD" } as const;

function Prose({ text }: { text: string }) {
    return <div onClick={handleCodeClick} dangerouslySetInnerHTML={{ __html: md(text) }} />;
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

/** The recent runs as bars (the tall green part is the share that passed); pick one to look at it. */
function RunHistory({ runs, selId, onPick }: { runs: CourseRun[]; selId: number; onPick: (id: number) => void }) {
    const shown = [...runs].reverse();
    return (
        <div className="cx-hist" role="group" aria-label="Recent runs">
            {shown.map((r) => (
                <button key={r.id} className={`cx-hbar${r.id === selId ? " on" : ""}`} aria-pressed={r.id === selId} onClick={() => onPick(r.id)} aria-label={`Run ${ago(r.at)}: ${r.problem ? "did not run" : `${r.passed} of ${r.total} passed`}`}>
                    <span className={`bar${r.problem ? " warn" : ""}`}>
                        <i style={{ height: r.problem ? "100%" : `${r.total ? Math.round((100 * r.passed) / r.total) : 0}%` }} />
                    </span>
                    <small>{r.problem ? "—" : `${r.passed}/${r.total}`}</small>
                    <em>{ago(r.at)}</em>
                </button>
            ))}
        </div>
    );
}

/** The Last run tab: the run history, and the chosen run (the newest unless you pick another). */
function RunTab({ runs, stageId }: { runs: CourseRun[]; stageId: string }) {
    const [sel, setSel] = useState<number | null>(null);
    const newest = runs[0];
    // A run that arrives while the tab is open brings you back to the newest.
    useEffect(() => setSel(null), [newest?.id]);
    if (!newest) return null;
    const run = runs.find((r) => r.id === sel) ?? newest;
    const prev = runs[runs.findIndex((r) => r.id === run.id) + 1];
    return (
        <>
            {runs.length > 1 && <RunHistory runs={runs} selId={run.id} onPick={setSel} />}
            <RunPanel key={run.id} run={run} stageId={stageId} prev={prev} />
        </>
    );
}

/** The Concepts tab: the reading for the stage, with what you have read and what is optional. */
function ConceptsTab({ course, page, queryKey }: { course: string; page: Page; queryKey: unknown[] }) {
    const qc = useQueryClient();
    const [flt, setFlt] = useState<"all" | "req" | "opt">("all");
    const [open, setOpen] = useState<string | null>(null);
    const mark = useMutation({
        mutationFn: ({ id, read }: { id: string; read: boolean }) => api.setConceptRead(course, id, read),
        onMutate: async ({ id, read }) => {
            // A poll that is already on its way would bring back the old value over this change.
            await qc.cancelQueries({ queryKey });
            qc.setQueryData<Page>(queryKey, (old) => old && { ...old, concepts: old.concepts.map((k) => (k.id === id ? { ...k, read } : k)) });
        },
        onSettled: () => qc.invalidateQueries({ queryKey }),
    });
    const req = page.concepts.filter((k) => k.required);
    const done = req.filter((k) => k.read).length;
    const left = req.filter((k) => !k.read).reduce((n, k) => n + k.minutes, 0);
    const list = page.concepts.filter((k) => flt === "all" || (flt === "req") === k.required);
    return (
        <>
            <div className="cx-chdr">
                <span className="cx-cring" style={{ "--p": req.length ? Math.round((100 * done) / req.length) : 100 } as React.CSSProperties} aria-hidden="true">
                    <span>
                        {done}/{req.length}
                    </span>
                </span>
                <div className="cx-chm">
                    <b>{req.length === 0 ? "Nothing required to read" : done === req.length ? "Required reading done" : `Required reading: ${done} of ${req.length} done`}</b>
                    <span>{req.length === 0 ? "These articles are further reading." : done === req.length ? "The optional articles go deeper when you want them." : `About ${left} minutes left. You can pass the stage without it; it saves you the hints.`}</span>
                </div>
                {page.concepts.some((k) => !k.required) && (
                    <div className="cx-rflt" role="group" aria-label="Show">
                        {([["all", "All"], ["req", "Required"], ["opt", "Optional"]] as const).map(([k, l]) => (
                            <button key={k} aria-pressed={flt === k} className={flt === k ? "on" : ""} onClick={() => setFlt(k)}>
                                {l}
                            </button>
                        ))}
                    </div>
                )}
            </div>
            {list.map((k) => (
                <article key={k.id} className={`cx-ccard${k.read ? " read" : ""}${open === k.id ? " open" : ""}`}>
                    <div className="cx-cch">
                        <span className="cx-cic" aria-hidden="true">
                            {k.read ? "✓" : page.concepts.indexOf(k) + 1}
                        </span>
                        <div className="cx-cbody">
                            <h4>
                                {k.title} <span className={`cx-cbadge ${k.required ? "req" : "opt"}`}>{k.required ? "REQUIRED" : "OPTIONAL"}</span>
                            </h4>
                            <p>{k.summary}</p>
                            <div className="cx-cmeta">
                                <span>{k.minutes} min read</span>
                                <span>{k.read ? "read" : "not read yet"}</span>
                            </div>
                        </div>
                        <div className="cx-cact">
                            <button className="kbtn sm sec" aria-expanded={open === k.id} onClick={() => setOpen(open === k.id ? null : k.id)}>
                                {open === k.id ? "Close" : "Preview"}
                            </button>
                            <Link className="kbtn sm" to="/courses/$course/concept/$id" params={{ course, id: k.id }}>
                                {k.read ? "Open" : "Read"} <span className="ar">›</span>
                            </Link>
                        </div>
                    </div>
                    <div className="cx-cprev">
                        <div inert={open !== k.id}>
                            <div className="cx-cfoot">
                                <label>
                                    <button type="button" role="switch" aria-checked={k.read} className="ksw" aria-label={`Mark "${k.title}" as read`} onClick={() => mark.mutate({ id: k.id, read: !k.read })} />
                                    Mark as read
                                </label>
                                <span>Opening the article does not mark it: you decide when you have read it.</span>
                            </div>
                        </div>
                    </div>
                </article>
            ))}
        </>
    );
}

/** The command that tests this stage, with a copy button. */
function StageCommand({ stageId }: { stageId: string }) {
    const [copied, setCopied] = useState(false);
    const cmd = `anneal course test ${stageId}`;
    const copy = () => {
        const done = () => {
            setCopied(true);
            setTimeout(() => setCopied(false), 1200);
        };
        try {
            navigator.clipboard.writeText(cmd).then(done, done);
        } catch {
            done();
        }
    };
    return (
        <div className="cx-cli">
            <span>test this stage</span>
            <code>{cmd}</code>
            <button onClick={copy}>{copied ? "COPIED" : "COPY"}</button>
        </div>
    );
}

/** The Run tab: a summary with one segment per test, failures first and open, passes folded, compiler output in its own block. */
function RunPanel({ run, stageId, prev }: { run: CourseRun; stageId: string; prev?: CourseRun }) {
    const failed = run.tests.map((t, i) => ({ ...t, i })).filter((t) => !t.ok);
    const passed = run.tests.filter((t) => t.ok);
    const [flt, setFlt] = useState<"all" | "bad" | "ok">("all");
    const [cmp, setCmp] = useState(false);
    const [open, setOpen] = useState(failed.length === 0 && !run.problem);
    const [copied, setCopied] = useState(false);
    // How each test of this run compares with the one before it, by name.
    const before = new Map((prev?.tests ?? []).map((t) => [t.name, t.ok]));
    const change = (name: string, ok: boolean) => (!prev || prev.problem || !before.has(name) ? "" : before.get(name) === ok ? "same" : ok ? "fixed" : "new");
    const prevPassed = prev && !prev.problem ? prev.passed : null;
    const delta = prev && !run.problem ? (prev.problem ? "first run that compiled" : null) : null;
    const newlyFailing = failed.filter((t) => change(t.name, false) === "new").length;
    const same = new Map<string, number>();
    for (const t of failed) same.set(t.detail.trim(), (same.get(t.detail.trim()) ?? 0) + 1);
    const first = failed[0];
    const cmd = run.problem ? `anneal course test ${stageId}` : first ? `anneal course test ${stageId} --only -f ${first.name}` : null;
    const copy = () => {
        const done = () => {
            setCopied(true);
            setTimeout(() => setCopied(false), 1200);
        };
        try {
            navigator.clipboard.writeText(cmd ?? "").then(done, done);
        } catch {
            done();
        }
    };
    const errors = run.problem ? (run.problem.match(/^error(\[|:)/gm) ?? []).length : 0;
    const tone = run.problem ? "warn" : failed.length > 0 ? "bad" : "ok";
    return (
        <>
            <div className={`cx-rsum ${tone}`}>
                <div className="cx-rtop">
                    <span className="cx-rbig">
                        {run.problem ? (
                            <em>Did not run</em>
                        ) : failed.length > 0 ? (
                            <>
                                <em>{failed.length} failed</em> · {passed.length} passed
                            </>
                        ) : (
                            <em>
                                {run.passed} of {run.total} passed
                            </em>
                        )}
                    </span>
                    <span className="cx-rmeta">
                        {ago(run.at)}
                        {run.commit_sha ? ` · commit ${run.commit_sha.slice(0, 7)}` : ""} · {(run.duration_ms / 1000).toFixed(1)}s
                    </span>
                </div>
                {!run.problem && run.tests.length > 0 && (
                    <div className="cx-rbar" aria-hidden>
                        {run.tests.map((t, i) => (
                            <i key={i} className={t.ok ? "" : "b"} />
                        ))}
                    </div>
                )}
                {!run.problem && prev && (
                    <div className="cx-rdelta">
                        {delta && <span className="eq">{delta}</span>}
                        {prevPassed !== null && run.passed > prevPassed && <span className="up">▲ {run.passed - prevPassed} more passing</span>}
                        {prevPassed !== null && run.passed < prevPassed && <span className="dn">▼ {prevPassed - run.passed} fewer passing</span>}
                        {prevPassed !== null && run.passed === prevPassed && <span className="eq">same result as the run before</span>}
                        {newlyFailing > 0 && <span className="dn">{newlyFailing} newly failing</span>}
                    </div>
                )}
                {cmd && (
                    <div className="cx-rcmd">
                        <span>{run.problem ? "compile locally" : "run again"}</span>
                        <code>{cmd}</code>
                        <button onClick={copy}>{copied ? "COPIED" : "COPY"}</button>
                    </div>
                )}
            </div>

            {!run.problem && run.tests.length > 0 && (
                <div className="cx-rtool">
                    <div className="cx-rflt" role="group" aria-label="Show">
                        {([["all", "All"], ["bad", "Failed"], ["ok", "Passed"]] as const).map(([k, l]) => (
                            <button key={k} aria-pressed={flt === k} className={flt === k ? "on" : ""} onClick={() => setFlt(k)}>
                                {l}
                            </button>
                        ))}
                    </div>
                    {prev && !prev.problem && (
                        <label className="cx-rcmp">
                            <button type="button" role="switch" aria-checked={cmp} className="ksw" onClick={() => setCmp(!cmp)} aria-label="Compare with the previous run" />
                            Compare with the previous run
                        </label>
                    )}
                </div>
            )}

            {run.problem && (
                <>
                    <div className="cx-rsec warn">COMPILER OUTPUT</div>
                    <div className="cx-rprob">
                        <div className="cx-rhead">
                            <span className="cx-sq" />
                            <span className="cx-tn">{errors > 0 ? `${errors} error${errors === 1 ? "" : "s"}` : "no tests ran"}</span>
                            <small>as the compiler printed it</small>
                        </div>
                        <pre>
                            {run.problem.split("\n").map((l, i) => (
                                <div key={i} className={/^error(\[|:)/.test(l) ? "er" : /^\s*-->/.test(l) ? "pt" : /^\s*(\d+\s*)?\|/.test(l) ? "dm" : undefined}>
                                    {l || " "}
                                </div>
                            ))}
                        </pre>
                    </div>
                </>
            )}

            {failed.length > 0 && flt !== "ok" && (
                <>
                    <div className="cx-rsec bad">FAILED · {failed.length}</div>
                    {failed.map((t) => {
                        const n = (same.get(t.detail.trim()) ?? 1) - 1;
                        return (
                            <div className="cx-rfail" key={t.name}>
                                <div className="cx-rhead">
                                    <span className="cx-sq" />
                                    <span className="cx-tn">{t.name}</span>
                                    {cmp && change(t.name, false) ? (
                                        <small className={`cx-rtag ${change(t.name, false) === "new" ? "new" : "same"}`}>{change(t.name, false) === "new" ? "NEWLY FAILING" : "STILL FAILING"}</small>
                                    ) : (
                                        <small>
                                            test {t.i + 1} of {run.tests.length}
                                        </small>
                                    )}
                                </div>
                                {t.detail && (
                                    <div className="cx-rbody">
                                        {n > 0 && (
                                            <p className="cx-rshared">
                                                same message as {n} other test{n === 1 ? "" : "s"}
                                            </p>
                                        )}
                                        <pre>{t.detail}</pre>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </>
            )}

            {passed.length > 0 && flt !== "bad" && (
                <>
                    <div className="cx-rsec ok">PASSED · {passed.length}</div>
                    <div className={`cx-rfold${open || flt === "ok" ? " open" : ""}`}>
                        <button className="cx-rfoldh" onClick={() => setOpen(!open)} aria-expanded={open || flt === "ok"}>
                            <span className="cx-sq" />
                            <span className="cx-tn">
                                {failed.length === 0 ? "all tests" : passed.length > 2 ? `${passed.slice(0, 2).map((t) => t.name).join(", ")} and ${passed.length - 2} more` : passed.map((t) => t.name).join(", ")}
                            </span>
                            <span className="cx-rchev">›</span>
                        </button>
                        {(open || flt === "ok") && (
                            <div className="cx-rlist">
                                {passed.map((t) => (
                                    <div className="cx-rrow" key={t.name}>
                                        <span className="cx-sq" />
                                        {t.name}
                                        {cmp && change(t.name, true) === "fixed" && <small className="cx-rtag fix">FIXED SINCE THE RUN BEFORE</small>}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </>
            )}
        </>
    );
}

function Sidebar({ course, page, panels }: { course: string; page: Page; panels: PanelsApi }) {
    const overview = useQuery({ queryKey: ["course", course], queryFn: () => api.course(course) });
    const o = overview.data;
    const here = page.module.code;
    // Modules open and close on their own; the one you are in is always open when you arrive in it.
    const [open, setOpen] = useState<Set<string>>(() => new Set([here]));
    useEffect(() => setOpen((prev) => (prev.has(here) ? prev : new Set(prev).add(here))), [here]);
    const [find, setFind] = useState("");
    const needle = find.trim().toLowerCase();
    const pct = o && o.total ? Math.round((100 * o.done) / o.total) : 0;
    const { p: pp, update, drawer, setDrawer } = panels;
    const toggle = (code: string) =>
        setOpen((prev) => {
            const next = new Set(prev);
            if (!next.delete(code)) next.add(code);
            return next;
        });
    const mine = o?.projects.flatMap((p) => p.modules).find((m) => m.code === here);
    // Bring the current stage into view in the tree (the tree scrolls, not the page).
    const tree = useRef<HTMLElement>(null);
    useEffect(() => {
        const box = tree.current;
        const leaf = box?.querySelector<HTMLElement>(".cx-leaf.cur");
        if (!box || !leaf) return;
        const top = leaf.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop;
        box.scrollTop = Math.max(0, top - box.clientHeight / 2);
    }, [page.stage.id, o]);
    return (
        <aside className={`cx-side${pp.lc ? " rail" : ""}${drawer === "l" ? " open" : ""}`} aria-label="Course">
            <Resizer side="l" panels={panels} />
            <div className="cx-sh2">
                <span className="cx-cring" style={{ "--p": pct } as React.CSSProperties} aria-hidden="true">
                    <span>{pct}%</span>
                </span>
                <div className="cx-shm">
                    <b>{page.course.title}</b>
                    <small>{o ? `${o.done} of ${o.total} stages passed` : ""}</small>
                </div>
                <button className="cx-pbtn cx-collapse" aria-label={pp.lc ? "Expand the course panel" : "Collapse the course panel"} title="Collapse (Ctrl/⌘ B)" onClick={() => update({ ...pp, lc: !pp.lc })}>
                    {pp.lc ? "»" : "«"}
                </button>
                <button className="cx-pbtn cx-dclose" aria-label="Close" onClick={() => setDrawer(null)}>
                    ×
                </button>
            </div>
            <label className="cx-sfind">
                <span aria-hidden="true">⌕</span>
                <input value={find} onChange={(e) => setFind(e.target.value)} placeholder="filter stages…" aria-label="Filter stages" autoComplete="off" spellCheck={false} onKeyDown={(e) => e.key === "Escape" && e.currentTarget.blur()} />
            </label>
            <nav className="cx-tree" aria-label="Course" ref={tree}>
                {o?.projects.map((p) => {
                    const mods = p.modules.filter((m) => !needle || m.stages.some((s) => `${s.title} ${s.id}`.toLowerCase().includes(needle)));
                    if (needle && mods.length === 0) return null;
                    return (
                        <Fragment key={p.number}>
                            <Link className={`cx-node${p.modules.length ? "" : " dim"}`} to="/courses/$course" params={{ course }}>
                                <span className="cx-nt">
                                    Project {p.number} · {p.title}
                                </span>
                                <span className="cx-nc">{p.modules.length ? `${p.modules.flatMap((m) => m.stages).filter((s) => s.state !== "todo").length}/${p.modules.flatMap((m) => m.stages).length}` : "planned"}</span>
                            </Link>
                            {mods.length > 0 && (
                                <div className="cx-kids">
                                    {mods.map((m) => {
                                        const isOpen = needle ? true : open.has(m.code);
                                        const leaves = needle ? m.stages.filter((s) => `${s.title} ${s.id}`.toLowerCase().includes(needle)) : m.stages;
                                        const done = m.stages.filter((s) => s.state !== "todo").length;
                                        return (
                                            <Fragment key={m.code}>
                                                <button className="cx-node cx-mrow" aria-expanded={isOpen} onClick={() => toggle(m.code)} disabled={!!needle}>
                                                    <span className="cx-car">{isOpen ? "▾" : "▸"}</span>
                                                    <span className="cx-nt">
                                                        {m.code} · {m.title}
                                                    </span>
                                                    <span className="cx-nc">
                                                        {done}/{m.stages.length}
                                                    </span>
                                                </button>
                                                <div className={`cx-mbody${isOpen ? " open" : ""}`}>
                                                    <div inert={!isOpen}>
                                                        <div className="cx-leaves">
                                                            {leaves.map((s: CourseStageRow) => (
                                                                <Link key={s.id} className={`cx-leaf${s.id === page.stage.id ? " cur" : ""}${s.kind === "boss" ? " boss" : ""}`} to="/courses/$course/$stage" params={{ course, stage: s.id }} onClick={() => setDrawer(null)}>
                                                                    <span className={`cx-si${s.state !== "todo" ? " ok" : s.id === page.stage.id ? " now" : ""}${s.state === "assisted" ? " asst" : ""}`} title={s.state === "assisted" ? "passed with help" : undefined}>{s.state !== "todo" ? "✓" : ""}</span>
                                                                    <span className="cx-ln2">{s.id.split("-")[1]}</span>
                                                                    <span className="cx-lt">{s.title}</span>
                                                                    <DifficultyBars d={s.difficulty} />
                                                                </Link>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </div>
                                            </Fragment>
                                        );
                                    })}
                                </div>
                            )}
                        </Fragment>
                    );
                })}
                {needle && !o?.projects.some((p) => p.modules.some((m) => m.stages.some((s) => `${s.title} ${s.id}`.toLowerCase().includes(needle)))) && <p className="cx-snone">No stage matches that.</p>}
            </nav>
            <div className="cx-rail" aria-label="This module">
                {mine?.stages.map((s) => (
                    <Link key={s.id} className={`cx-rdot${s.id === page.stage.id ? " cur" : ""}`} to="/courses/$course/$stage" params={{ course, stage: s.id }} title={`${s.id.split("-")[1]} · ${s.title}`} aria-label={s.title}>
                        <span className={`cx-si${s.state !== "todo" ? " ok" : s.id === page.stage.id ? " now" : ""}${s.state === "assisted" ? " asst" : ""}`}>{s.state !== "todo" ? "✓" : ""}</span>
                    </Link>
                ))}
            </div>
        </aside>
    );
}

/** Sections that go beyond what passing the stage needs; they can be hidden. */
const OPTIONAL_SECTIONS = new Set(["performance", "learn-more"]);

/** Three small bars for the difficulty: one lit for easy, two for medium, three for hard. */
function DifficultyBars({ d }: { d: StageDifficulty }) {
    const n = d === "hard" ? 3 : d === "medium" ? 2 : 1;
    return (
        <span className="cx-dbars" style={{ color: DIFFICULTY_COLOR[d] }} title={d}>
            <i className={n >= 1 ? "on" : ""} />
            <i className={n >= 2 ? "on" : ""} />
            <i className={n >= 3 ? "on" : ""} />
        </span>
    );
}

export function CourseStagePage({ course, stage }: { course: string; stage: string }) {
    const qc = useQueryClient();
    const nav = useNavigate();
    const panels = usePanels();
    const key = ["course-stage", course, stage];
    // Poll while the page is open and visible: a push in the terminal shows up here within a few seconds.
    const q = useQuery({ queryKey: key, queryFn: () => api.courseStage(course, stage), refetchInterval: 3000 });
    const set = (p: Page) => {
        qc.setQueryData(key, p);
        qc.invalidateQueries({ queryKey: ["course", course] });
    };
    const hint = useMutation({ mutationFn: () => api.revealCourseHint(course, stage), onSuccess: set });
    const sol = useMutation({ mutationFn: () => api.revealCourseSolution(course, stage), onSuccess: set });
    const p = q.data;
    const [active, setActive] = useState("s-top");
    const [toast, setToast] = useState<{ ok: boolean; text: string } | null>(null);
    // The tests-passed popup (unless "don't show again" is on, then the toast below says it).
    const [win, setWin] = useState(false);
    // Sidenotes written in the text (`^[...]`): shown in the page panel, numbered in the order they appear.
    const [notes, setNotes] = useState<{ n: number; html: string }[]>([]);
    const [selNote, setSelNote] = useState<number | null>(null);
    const [curNote, setCurNote] = useState<number | null>(null);
    // Optional sections (Performance, Learn more): shown unless you chose to hide them; each can be flipped on its own.
    const [optHidden, setOptHidden] = useState<boolean>(() => getPref("optional.hidden", false));
    const [flipped, setFlipped] = useState<Set<string>>(() => new Set());
    const seenRun = useRef<number | null>(null);
    const tabFromHash = (): Tab => {
        const h = location.hash.slice(1);
        return (["instructions", "hints", "solution", "concepts", "run"] as const).find((x) => x === h) ?? "instructions";
    };
    const [tab, setTab] = useState<Tab>(tabFromHash);
    // Each tab keeps its own scroll position, so going to Hints and back returns to where you were reading.
    const scrolls = useRef<Partial<Record<Tab, number>>>({});
    const restore = useRef<number | null>(null);
    const pick = (k: Tab) => {
        scrolls.current[tab] = window.scrollY;
        restore.current = scrolls.current[k] ?? 0;
        setTab(k);
        // A hash on every tab: dropping it makes the router treat the change as a new page and scroll to the top.
        history.replaceState(null, "", `#${k}`);
    };
    // After the new tab is in the page: scrolling earlier would be clamped to the height of the tab being left.
    useLayoutEffect(() => {
        if (restore.current === null) return;
        window.scrollTo({ top: restore.current });
        restore.current = null;
    }, [tab]);

    useEffect(() => {
        window.scrollTo({ top: 0 });
    }, [stage]);
    // A run that arrives while the page is open (or one from the last half minute) pops a result: "Tests passed, proceed" or the count.
    const lastRun = p?.last_run ?? null;
    useEffect(() => {
        if (!lastRun) return;
        const first = seenRun.current === null;
        if (seenRun.current === lastRun.id) return;
        seenRun.current = lastRun.id;
        const fresh = Date.now() - new Date(lastRun.at).getTime() < 30_000;
        if (first && !fresh) return;
        qc.invalidateQueries({ queryKey: ["course", course] });
        if (lastRun.ok && !celebrateOff()) {
            setWin(true);
            return;
        }
        setToast(
            lastRun.ok
                ? { ok: true, text: "Tests passed" }
                : { ok: false, text: lastRun.problem ? "The tests did not run" : `${lastRun.passed} of ${lastRun.total} passing` },
        );
        if (!lastRun.ok) {
            const t = setTimeout(() => setToast(null), 9000);
            return () => clearTimeout(t);
        }
    }, [lastRun?.id]); // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            if (e.metaKey || e.ctrlKey || e.altKey || (e.target as HTMLElement | null)?.closest("input, textarea, [contenteditable]")) return;
            const to = e.key === "[" ? p?.prev : e.key === "]" ? p?.next : null;
            if (to) nav({ to: "/courses/$course/$stage", params: { course, stage: to.id } });
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [p, course, nav]);
    const ids = p ? ["s-top", ...p.stage.sections.map((s) => `sec-${s.id}`)] : [];
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

    // Number the sidenote markers on the page and collect their text for the panel.
    useEffect(() => {
        const found: { n: number; html: string }[] = [];
        document.querySelectorAll<HTMLElement>(".cx-col .cx-snm").forEach((m, i) => {
            m.textContent = String(i + 1);
            m.dataset.sn = String(i + 1);
            const body = m.nextElementSibling;
            if (body instanceof HTMLElement && body.classList.contains("cx-snb")) {
                body.dataset.sn = String(i + 1);
                found.push({ n: i + 1, html: body.innerHTML });
            }
        });
        setNotes((prev) => (JSON.stringify(prev) === JSON.stringify(found) ? prev : found));
    });
    // A marker opens its note in the panel, or under the paragraph when the panel is not on screen.
    useEffect(() => {
        const open = (m: HTMLElement) => {
            const n = Number(m.dataset.sn);
            if (window.innerWidth > 1100 && !panels.p.rc) {
                setSelNote((cur) => (cur === n ? null : n));
                document.querySelector(`.cx-pnote[data-sn="${n}"]`)?.scrollIntoView({ block: "nearest", behavior: "smooth" });
            } else {
                const on = m.nextElementSibling?.classList.toggle("open");
                m.setAttribute("aria-expanded", String(!!on));
            }
        };
        const onClick = (e: MouseEvent) => {
            const m = (e.target as HTMLElement).closest<HTMLElement>(".cx-snm");
            if (m) open(m);
        };
        const onKey = (e: KeyboardEvent) => {
            const m = (e.target as HTMLElement).closest<HTMLElement>(".cx-snm");
            if (m && (e.key === "Enter" || e.key === " ")) (e.preventDefault(), open(m));
        };
        document.addEventListener("click", onClick);
        document.addEventListener("keydown", onKey);
        return () => {
            document.removeEventListener("click", onClick);
            document.removeEventListener("keydown", onKey);
        };
    }, [panels.p.rc]);
    // The note for the text you are reading stands out in the panel.
    useEffect(() => {
        if (notes.length === 0) return;
        const onScroll = () => {
            let cur: number | null = null;
            for (const m of document.querySelectorAll<HTMLElement>(".cx-col .cx-snm")) {
                const top = m.getBoundingClientRect().top;
                if (top < window.innerHeight * 0.55) cur = Number(m.dataset.sn);
                if (top >= window.innerHeight * 0.55) break;
            }
            setCurNote(cur);
        };
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
        return () => window.removeEventListener("scroll", onScroll);
    }, [notes.length]);

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
    const toc: [string, string][] = [["s-top", "Overview"], ...p.stage.sections.map((s): [string, string] => [`sec-${s.id}`, s.title])];
    const tabs: [Tab, string, string][] = [
        ["instructions", "Instructions", ""],
        ["hints", "Hints", p.hints.total ? `${p.hints.revealed.length}/${p.hints.total}` : ""],
        ["solution", "Solution", ""],
        ["concepts", "Concepts", p.concepts.length ? `${p.concepts.filter((k) => k.required && k.read).length}/${p.concepts.filter((k) => k.required).length}` : ""],
        ["run", "Last run", run ? (run.ok ? "✓" : `${run.passed}/${run.total}`) : ""],
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
                    {(panels.p.lc || panels.p.rc) && (
                        <span className="cx-reopen">
                            {panels.p.lc && (
                                <button onClick={() => panels.update({ ...panels.p, lc: false })} aria-label="Show the course panel" title="Show the course panel (Ctrl/⌘ B)">
                                    ☰
                                </button>
                            )}
                            {panels.p.rc && (
                                <button onClick={() => panels.update({ ...panels.p, rc: false })} aria-label="Show the page panel" title="Show the page panel (Ctrl/⌘ .)">
                                    ▤
                                </button>
                            )}
                        </span>
                    )}
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
            {win && lastRun?.ok && (
                <Celebration
                    title="Stage passed"
                    message={`All ${lastRun.total} tests pass.${p.hints.revealed.length === 0 ? " Nicely done: no hints used." : ""}`}
                    stats={[
                        { value: `${lastRun.passed}/${lastRun.total}`, label: "tests" },
                        { value: `${(lastRun.duration_ms / 1000).toFixed(1)}s`, label: "run time" },
                        { value: String(p.hints.revealed.length), label: "hints" },
                    ]}
                    next={p.next ? { kicker: "NEXT STAGE", title: p.next.title } : undefined}
                    goLabel={p.next ? "Go to next stage" : "Back to the course"}
                    onGo={() => {
                        setWin(false);
                        if (p.next) nav({ to: "/courses/$course/$stage", params: { course, stage: p.next.id } });
                        else nav({ to: "/courses/$course", params: { course } });
                    }}
                    review={p.solution.available ? { label: "Review solution", onReview: () => (setWin(false), pick("solution")) } : undefined}
                    onClose={() => setWin(false)}
                />
            )}
            {toast && (
                <div className={`cx-toast ${toast.ok ? "ok" : "bad"}`} role="status">
                    <i>{toast.ok ? "✓" : "!"}</i>
                    <b>{toast.text}</b>
                    {toast.ok && p.next && (
                        <Link to="/courses/$course/$stage" params={{ course, stage: p.next.id }} onClick={() => setToast(null)}>
                            Proceed to {p.next.title} →
                        </Link>
                    )}
                    {toast.ok && !p.next && <span>That was the last stage.</span>}
                    {!toast.ok && <button onClick={() => { pick("run"); setToast(null); }}>see details</button>}
                    <button className="x" aria-label="Dismiss" onClick={() => setToast(null)}>×</button>
                </div>
            )}
            <div className="cx-mbar">
                <button onClick={() => panels.setDrawer(panels.drawer === "l" ? null : "l")} aria-expanded={panels.drawer === "l"}>
                    ☰ Stages <b>{p.module.stages.findIndex((s) => s.id === p.stage.id) + 1}/{p.module.stages.length}</b>
                </button>
                <button onClick={() => panels.setDrawer(panels.drawer === "r" ? null : "r")} aria-expanded={panels.drawer === "r"}>
                    ▤ This page
                </button>
            </div>
            {panels.drawer && <div className="cx-dbk" onClick={() => panels.setDrawer(null)} aria-hidden="true" />}
            <div
                className={`cx${panels.dragging ? " dragging" : ""}${panels.p.lc ? " lc" : ""}${panels.p.rc ? " rc" : ""}`}
                style={{ "--ca": "var(--grn)", "--cab": "var(--grn-bg)", "--cl": panels.p.lc ? "64px" : `${panels.p.l}px`, "--cr": panels.p.rc ? "0px" : `${panels.p.r}px` } as React.CSSProperties}
            >
                <Sidebar course={course} page={p} panels={panels} />
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
                            <StageCommand stageId={p.stage.id} />
                            {p.stage.learn.length > 0 && (
                                <div className="cx-learn">
                                    <span className="lab">YOU'LL LEARN</span>
                                    {p.stage.learn.map((l) => (
                                        <span className="cpill" key={l}>
                                            {l}
                                        </span>
                                    ))}
                                </div>
                            )}
                            <div className="cx-tabs" role="tablist" aria-label="Stage">
                                {tabs.map(([k, label, n]) => (
                                    <button key={k} role="tab" aria-selected={tab === k} className={tab === k ? "on" : ""} onClick={() => pick(k)}>
                                        {label}
                                        {n !== "" && <small>{n}</small>}
                                    </button>
                                ))}
                            </div>

                            {tab === "instructions" && (
                                <div className="cx-prose">
                                    {p.concepts.length > 0 && (
                                        <button className="cx-readfirst" onClick={() => pick("concepts")}>
                                            <b>READ FIRST</b>
                                            <span>
                                                {p.concepts[0]?.title}
                                                {p.concepts.length > 1 && <> · and {p.concepts.length - 1} more</>} <em>~{p.concepts.reduce((n, k) => n + k.minutes, 0)} min</em>
                                            </span>
                                            <i>open ›</i>
                                        </button>
                                    )}
                                    {p.stage.intro && (
                                        <div className="cx-leadmd">
                                            <Prose text={p.stage.intro} />
                                        </div>
                                    )}
                                    {p.stage.sections.map((s, i) => {
                                        const part = /^Part (\d+) · (.*)$/.exec(s.title);
                                        const optional = OPTIONAL_SECTIONS.has(s.id);
                                        const shut = optional && optHidden !== flipped.has(s.id);
                                        return (
                                            <section key={s.id} id={`sec-${s.id}`}>
                                                <div className="cx-part">
                                                    <b>{part ? `PART ${part[1]}` : String(i + 1).padStart(2, "0")}</b>
                                                    {part ? "" : s.title.toUpperCase()}
                                                </div>
                                                {part && <h2>{part[2]}</h2>}
                                                {optional && (
                                                    <div className="cx-oh">
                                                        <span className="cx-obadge">OPTIONAL</span>
                                                        <button aria-expanded={!shut} onClick={() => setFlipped((f) => { const n = new Set(f); if (!n.delete(s.id)) n.add(s.id); return n; })}>
                                                            {shut ? "SHOW" : "HIDE"}
                                                        </button>
                                                    </div>
                                                )}
                                                {optional ? (
                                                    <div className={`cx-obody${shut ? " shut" : ""}`}>
                                                        <div inert={shut}>
                                                            <Body text={s.md} />
                                                        </div>
                                                    </div>
                                                ) : s.title === "The task" ? (
                                                    <div className="cx-task">
                                                        <div className="cx-th">
                                                            <b>YOUR TURN</b>
                                                            <span>
                                                                run <kbd>anneal course test</kbd> or push
                                                            </span>
                                                        </div>
                                                        <div className="cx-tb cx-prose">
                                                            <Prose text={s.md} />
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <Body text={s.md} />
                                                )}
                                            </section>
                                        );
                                    })}
                                </div>
                            )}

                            {tab === "hints" && (
                                <div className="cx-prose">
                                    {p.hints.total === 0 ? (
                                        <div className="cx-empty">No hints written for this stage yet.</div>
                                    ) : (
                                        <>
                                            <p className="cx-quiet" style={{ margin: "0 0 4px" }}>
                                                {p.hints.revealed.length} of {p.hints.total} opened. Each hint opened before the stage passes marks it as assisted. They get deeper: the first nudges the design, the last names the invariant to check.
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
                                        </>
                                    )}
                                </div>
                            )}

                            {tab === "solution" && (
                                <div className="cx-prose">
                                    {p.solution.open && p.solution.files ? (
                                        <>
                                            <p className="cx-quiet" style={{ margin: 0 }}>
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
                                </div>
                            )}

                            {tab === "concepts" && (
                                <div className="cx-prose">
                                    {p.concepts.length > 0 && <ConceptsTab course={course} page={p} queryKey={key} />}
                                    <div className="cx-part">
                                        <b>FURTHER READING</b>
                                        {p.module.code.toUpperCase()} · {p.module.title.toUpperCase()}
                                    </div>
                                    <div className="cx-reads">
                                        {p.module.lectures.map((l) => (
                                            <a key={l.id} href={l.video ?? l.slides} target="_blank" rel="noreferrer">
                                                <small>CMU 15-445 LECTURE · {l.term.toUpperCase()}</small>
                                                {l.title}
                                                <span>{[l.slides && "slides", l.notes && "notes", l.video && "video"].filter(Boolean).join(" · ")}</span>
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
                                </div>
                            )}

                            {tab === "run" && (
                                <div className="cx-prose">
                                    {run ? (
                                        <RunTab runs={p.runs.length ? p.runs : [run]} stageId={p.stage.id} />
                                    ) : (
                                        <div className="cx-empty">
                                            No run yet. In your repo, run <code>anneal course test</code>, or commit and push: each run is reported here.
                                        </div>
                                    )}
                                </div>
                            )}
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
                                <button onClick={() => pick("run")}>show logs</button>
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
                <aside className={`cx-toc${panels.drawer === "r" ? " open" : ""}`} aria-label="This page">
                    <Resizer side="r" panels={panels} />
                    <div className="cx-tscroll">
                        {tab === "instructions" && (
                            <section className="cx-card">
                                <h4>
                                    <span>ON THIS PAGE</span>
                                    <button className="cx-pbtn cx-collapse" aria-label="Hide the page panel" title="Hide (Ctrl/⌘ .)" onClick={() => panels.update({ ...panels.p, rc: true })}>
                                        »
                                    </button>
                                    <button className="cx-pbtn cx-dclose" aria-label="Close" onClick={() => panels.setDrawer(null)}>
                                        ×
                                    </button>
                                </h4>
                                <div className="cx-outline">
                                    {toc.map(([id, label]) => (
                                        <a
                                            key={id}
                                            href={`#${id}`}
                                            className={active === id ? "on" : ""}
                                            onClick={(e) => {
                                                e.preventDefault();
                                                panels.setDrawer(null);
                                                // a hidden optional section opens when you go to it
                                                const sid = id.replace(/^sec-/, "");
                                                if (OPTIONAL_SECTIONS.has(sid) && optHidden !== flipped.has(sid)) setFlipped((f) => { const n = new Set(f); if (!n.delete(sid)) n.add(sid); return n; });
                                                setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" }), 0);
                                            }}
                                        >
                                            {label}
                                        </a>
                                    ))}
                                </div>
                                {p.stage.sections.some((x) => OPTIONAL_SECTIONS.has(x.id)) && (
                                    <button className="cx-ocontrol" onClick={() => { setOptHidden(!optHidden); setPref("optional.hidden", !optHidden); setFlipped(new Set()); }}>
                                        {optHidden ? "SHOW OPTIONAL SECTIONS" : "HIDE OPTIONAL SECTIONS"}
                                    </button>
                                )}
                            </section>
                        )}
                        {notes.length > 0 && tab === "instructions" && (
                            <section className="cx-card" aria-label="Notes">
                                <h4>
                                    <span>NOTES</span>
                                    <span className="cx-count">{notes.length}</span>
                                </h4>
                                {notes.map((n) => (
                                    <div
                                        key={n.n}
                                        role="button"
                                        tabIndex={0}
                                        data-sn={n.n}
                                        className={`cx-pnote${curNote === n.n ? " cur" : ""}${selNote === n.n ? " sel" : ""}`}
                                        onClick={(e) => {
                                            if ((e.target as HTMLElement).closest("a")) return;
                                            setSelNote((cur) => (cur === n.n ? null : n.n));
                                            document.querySelector(`.cx-snm[data-sn="${n.n}"]`)?.scrollIntoView({ behavior: "smooth", block: "center" });
                                        }}
                                        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), (e.currentTarget as HTMLElement).click())}
                                    >
                                        <b>{n.n}</b>
                                        <span dangerouslySetInnerHTML={{ __html: n.html }} />
                                    </div>
                                ))}
                            </section>
                        )}
                        {p.concepts.length > 0 && (
                            <section className="cx-card">
                                <h4>
                                    <span>CONCEPTS</span>
                                    <button className="cx-pbtn cx-link" onClick={() => (pick("concepts"), panels.setDrawer(null))}>
                                        {p.concepts.length} ›
                                    </button>
                                </h4>
                                {p.concepts.map((k) => (
                                    <Link key={k.id} className={`cx-crow${k.read ? " read" : ""}`} to="/courses/$course/concept/$id" params={{ course, id: k.id }}>
                                        <b>
                                            {k.read && <span className="cx-rtick" aria-label="read">✓ </span>}
                                            {k.title}
                                        </b>
                                        <small>
                                            {k.minutes} min read{k.required ? "" : " · optional"}
                                        </small>
                                    </Link>
                                ))}
                            </section>
                        )}
                        <section className="cx-card">
                            <h4>
                                <span>THIS STAGE</span>
                            </h4>
                            <div className="cx-cmdline">
                                <code>anneal course test {p.stage.id}</code>
                                <CopyButton text={`anneal course test ${p.stage.id}`} />
                            </div>
                            <div className="cx-kv">
                                <span>Last run</span>
                                <b>{p.last_run ? (p.last_run.problem ? "did not run" : `${p.last_run.passed} / ${p.last_run.total} · ${ago(p.last_run.at)}`) : "none yet"}</b>
                            </div>
                            <div className="cx-kv">
                                <span>Hints used</span>
                                <b>
                                    {p.hints.revealed.length} / {p.hints.total}
                                </b>
                            </div>
                            <p className="cx-keys">
                                <kbd>[</kbd> <kbd>]</kbd> previous / next stage
                            </p>
                        </section>
                    </div>
                    <FocusTimer />
                </aside>
            </div>
        </>
    );
}
