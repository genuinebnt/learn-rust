import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState, type CSSProperties, type ReactNode } from "react";
import { api, type DsaProblem, type Grade } from "../api";
import { Companies, Md, Mark, PyCode, useLogger } from "../components/dsaBits";
import { Header } from "../components/Header";
import { DIFF, MINUTES, inDays, leetcode, niceDate, statusOf, videoUrl } from "../dsa";

const LIST_NAME = { blind75: "Blind 75", neetcode150: "NeetCode 150", neetcode250: "NeetCode 250", all: "NeetCode All", practice: "Practice" };
const SAME_IDEA_SHOWN = 7;
/** The four log tiles: short labels, since each one also says when the problem comes back. */
const TILES: { grade: Grade; glyph: string; label: string; cls: string }[] = [
    { grade: "good", glyph: "✓", label: "On my own", cls: "ok" },
    { grade: "hard", glyph: "½", label: "With help", cls: "half" },
    { grade: "again", glyph: "✗", label: "Not yet", cls: "no" },
    { grade: "easy", glyph: "⚡", label: "Instant", cls: "fast" },
];

const dotOf = (p: DsaProblem) => (p.state.last_grade ? (p.state.last_grade === "again" ? "fail" : p.state.last_grade === "hard" ? "help" : "solo") : "");

/** A NeetCode problem: the statement and lesson on the left, every action in a sticky rail on the right. */
export function DsaProblemPage({ slug }: { slug: string }) {
    const overview = useQuery({ queryKey: ["dsa"], queryFn: api.dsa });
    const o = overview.data;
    const { log, toast, busy } = useLogger(o?.today);
    const p = o?.problems.find((x) => x.slug === slug);
    const lesson = useQuery({ queryKey: ["dsa-page", p?.id], queryFn: () => api.dsaPage(p!.id), enabled: !!p?.has_page });
    const statement = useQuery({ queryKey: ["dsa-statement", p?.id], queryFn: () => api.statement(p!.id), enabled: !!p, staleTime: Infinity, retry: false });
    const preview = useQuery({ queryKey: ["dsa-preview", p?.id], queryFn: () => api.preview(p!.id), enabled: !!p });
    const [tab, setTab] = useState(0);
    const [hintsShown, setHintsShown] = useState(0);
    const [more, setMore] = useState(false);
    const [section, setSection] = useState("problem");
    const hasHints = (statement.data?.hints.length ?? 0) > 0;
    const hasLesson = !!lesson.data;
    const sections = [
        { id: "problem", label: "Problem" },
        ...(hasHints ? [{ id: "hints", label: "Hints" }] : []),
        { id: "idea", label: "Idea" },
        ...(hasLesson ? [{ id: "approaches", label: "Approaches" }, { id: "tips", label: "Tips" }] : []),
    ];
    const ids = sections.map((s) => s.id).join();

    // The sub-nav follows the reader: the last section whose top has scrolled past the top of the page.
    useEffect(() => {
        const onScroll = () => {
            let current = "problem";
            for (const id of ids.split(",")) {
                const el = document.getElementById(`pp-${id}`);
                if (el && el.getBoundingClientRect().top < 140) current = id;
            }
            setSection(current);
        };
        onScroll();
        window.addEventListener("scroll", onScroll, { passive: true });
        return () => window.removeEventListener("scroll", onScroll);
    }, [ids]);

    const frame = (body: ReactNode) => (
        <>
            <Header area="dsa" />
            <main className="page pp" style={{ "--ca": "var(--acc)", "--cab": "var(--acc-bg)" } as CSSProperties}>
                {body}
            </main>
            {toast}
        </>
    );
    if (!o) return frame(<p className="rempty pp-pad">{overview.isError ? "Couldn't reach the API." : "Loading…"}</p>);
    if (!p) return frame(<p className="notice bad pp-pad">No NeetCode problem called {slug}. <Link to="/dsa">Back to the list</Link></p>);

    const pattern = o.patterns.find((x) => x.code === p.pattern);
    const technique = o.techniques.find((t) => t.id === p.technique);
    const teacher = p.practice_of ? o.problems.find((x) => x.id === p.practice_of) : undefined;
    const mustLearn = technique ? o.problems.find((x) => x.id === technique.must_learn) : undefined;
    const sameIdea = technique ? o.problems.filter((x) => x.technique === technique.id).sort((a, b) => a.order - b.order) : [];
    const inPattern = o.problems.filter((x) => x.pattern === p.pattern).sort((a, b) => a.order - b.order);
    const at = inPattern.findIndex((x) => x.id === p.id);
    const prev = at > 0 ? inPattern[at - 1] : undefined;
    const next = at >= 0 && at < inPattern.length - 1 ? inPattern[at + 1] : undefined;
    const status = statusOf(p, o.today);
    const s = p.state;
    const previews = preview.data?.previews;
    const recall = s.retrievability != null ? Math.round(s.retrievability * 100) : null;
    const today = o.today;
    const go = (id: string) => document.getElementById(`pp-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
    const gradeNote = (g: Grade) => {
        if (previews === undefined) return "…";
        if (previews === null) return "no review";
        const v = previews[g];
        return v.days === 0 ? "back today" : `back ${inDays(v.days)}`;
    };
    const standing = s.last_grade
        ? status === "due"
            ? [`Review due ${s.due && s.due < today ? "now" : "today"}`, `${s.reps} log${s.reps === 1 ? "" : "s"} · ${s.lapses} lapse${s.lapses === 1 ? "" : "s"}`]
            : s.last_grade === "again"
                ? ["Couldn't solve it yet", s.due ? `Retry ${niceDate(s.due, today)}` : "Retry soon"]
                : [s.last_grade === "hard" ? "Solved with help" : "Solved on my own", s.due ? `Next review ${niceDate(s.due, today)}` : `${s.reps} logs`]
        : ["Not logged yet", "Solve it on LeetCode, then log how it went. The next review is scheduled for you."];
    const lists = p.lists.filter((l) => l !== "practice" || p.lists.length === 1).map((l) => LIST_NAME[l]);

    return frame(
        <>
            <div className="pp-band">
                <div className="pp-in">
                    <div className="pp-crumbs">
                        <Link to="/dsa">DSA</Link>
                        <span>/</span>
                        {pattern ? <Link to="/dsa/patterns/$code" params={{ code: pattern.code }}>{pattern.name.toUpperCase()}</Link> : <span>?</span>}
                        <span>/</span>
                        <span>#{p.number}</span>
                    </div>
                    <div className="pp-titlerow">
                        <Mark p={p} today={today} />
                        <h1>{p.title}</h1>
                    </div>
                    <div className="pp-badges">
                        <span className="pp-b" style={{ color: DIFF[p.difficulty][1] }}><i />{DIFF[p.difficulty][0]}</span>
                        {p.role === "must_learn" ? <span className="pp-b must">MUST LEARN</span> : <span className="pp-b">PRACTICE</span>}
                        {p.premium && <span className="pp-b prem">PREMIUM</span>}
                        <span className="pp-b">~{MINUTES[p.difficulty]} min</span>
                        {lists.map((l) => <span key={l} className="pp-b">{l}</span>)}
                        {technique && <span className="pp-b tech">{technique.name}</span>}
                    </div>
                    {p.tags.length > 0 && <div className="pp-tags">{p.tags.map((t) => <span key={t}>{t}</span>)}</div>}
                    <nav className="pp-subnav" aria-label="Sections">
                        {sections.map((x) => (
                            <button key={x.id} className={section === x.id ? "on" : ""} aria-current={section === x.id} onClick={() => go(x.id)}>{x.label}</button>
                        ))}
                    </nav>
                </div>
            </div>

            <div className="pp-cols">
                <div className="pp-main">
                    <section className="pp-sec" id="pp-problem">
                        <h3><span>PROBLEM</span><em>from LeetCode{statement.data?.stale ? ", an older copy" : ""}</em></h3>
                        {statement.isLoading && <p className="rempty">Fetching the statement from LeetCode…</p>}
                        {statement.isError && (
                            <p className="rempty">
                                Couldn't fetch the statement from LeetCode right now. <a href={leetcode(p.slug)} target="_blank" rel="noreferrer" style={{ color: "var(--ca)" }}>Read it on LeetCode ↗</a>
                            </p>
                        )}
                        {statement.data?.locked && (
                            <p className="rempty">
                                This is a LeetCode Premium problem, so LeetCode doesn't share its statement. <a href={leetcode(p.slug)} target="_blank" rel="noreferrer" style={{ color: "var(--ca)" }}>Open it on LeetCode ↗</a>
                            </p>
                        )}
                        {statement.data?.html && <div className="d-statement" dangerouslySetInnerHTML={{ __html: statement.data.html }} />}
                    </section>

                    {hasHints && statement.data && (
                        <section className="pp-sec" id="pp-hints">
                            <h3><span>HINTS</span><em>LeetCode's, one at a time</em></h3>
                            <div className="d-hints">
                                {statement.data.hints.map((h, i) =>
                                    i < hintsShown ? (
                                        <div key={i} className="d-hint open">
                                            <b>Hint {i + 1}</b>
                                            <div className="d-statement" dangerouslySetInnerHTML={{ __html: h }} />
                                        </div>
                                    ) : (
                                        <button key={i} className="d-hint" disabled={i > hintsShown} onClick={() => setHintsShown(i + 1)}>
                                            <b>Hint {i + 1}</b>
                                            <span>{i === hintsShown ? "click to reveal" : "reveal the one before first"}</span>
                                        </button>
                                    ),
                                )}
                            </div>
                        </section>
                    )}

                    <section className="pp-sec" id="pp-idea">
                        <h3><span>THE IDEA</span>{technique && <em>{technique.name}</em>}</h3>
                        {technique && (
                            <p className="pp-lead">
                                <b>{technique.name}</b>.{" "}
                                {p.role === "must_learn" ? "This is the problem that teaches it first." : teacher ? <>Practice for <Link to="/d/$slug" params={{ slug: teacher.slug }} style={{ color: "var(--ca)" }}>{teacher.title}</Link>, which teaches it.</> : null}{" "}
                                {technique.problems} problem{technique.problems === 1 ? "" : "s"} use it.
                                {pattern && <> <Link to="/dsa/patterns/$code" params={{ code: pattern.code }} style={{ color: "var(--ca)" }}>Read the {pattern.name} lesson ›</Link></>}
                            </p>
                        )}
                        {mustLearn && mustLearn.id !== p.id && !teacher && (
                            <p className="pp-lead">Starts with <Link to="/d/$slug" params={{ slug: mustLearn.slug }} style={{ color: "var(--ca)" }}>{mustLearn.title}</Link>.</p>
                        )}
                        {lesson.data && <Md text={lesson.data.intuition} />}
                        {!p.has_page && <p className="rempty">The written lesson for this problem isn't written yet. Solve it on LeetCode and log how it went.</p>}
                    </section>

                    {lesson.data && (
                        <>
                            <section className="pp-sec" id="pp-approaches">
                                <h3><span>APPROACHES</span><em>Python, pastes into LeetCode</em></h3>
                                <div className="pp-tabs" role="tablist">
                                    {lesson.data.approaches.map((a, i) => (
                                        <button key={a.name} role="tab" aria-selected={i === tab} className={i === tab ? "on" : ""} onClick={() => setTab(i)}>{a.label}</button>
                                    ))}
                                </div>
                                {lesson.data.approaches.map((a, i) =>
                                    i === tab ? (
                                        <div key={a.name} className="d-ap">
                                            <h3 className="pp-apname">{a.name}</h3>
                                            <Md text={a.idea} />
                                            <PyCode code={a.code} />
                                            <div className="pp-cx">
                                                <span>time <b>{a.time}</b></span>
                                                <span>space <b>{a.space}</b></span>
                                            </div>
                                            {(a.time_why || a.space_why || a.note) && (
                                                <dl className="pp-why">
                                                    {a.time_why && <><dt>Why time is {a.time}</dt><dd><Md inline text={a.time_why} /></dd></>}
                                                    {a.space_why && <><dt>Why space is {a.space}</dt><dd><Md inline text={a.space_why} /></dd></>}
                                                    {a.note && <><dt>Note</dt><dd><Md inline text={a.note} /></dd></>}
                                                </dl>
                                            )}
                                        </div>
                                    ) : null,
                                )}
                            </section>
                            <section className="pp-sec" id="pp-tips">
                                <h3><span>TIPS AND PITFALLS</span></h3>
                                <ul className="d-tips">
                                    {lesson.data.tips.map((t) => (
                                        <li key={t}><Md inline text={t} /></li>
                                    ))}
                                </ul>
                            </section>
                        </>
                    )}

                    {(prev || next) && (
                        <div className="pp-pn">
                            {prev ? <Link to="/d/$slug" params={{ slug: prev.slug }}><small>← PREVIOUS IN {pattern?.name.toUpperCase()}</small><b>{prev.title}</b></Link> : <span />}
                            {next ? <Link to="/d/$slug" params={{ slug: next.slug }}><small>NEXT IN {pattern?.name.toUpperCase()} →</small><b>{next.title}</b></Link> : <span />}
                        </div>
                    )}
                </div>

                <aside className="pp-rail">
                    <div className="pp-card">
                        <a className="pp-act pri" href={leetcode(p.slug)} target="_blank" rel="noreferrer">Solve on LeetCode ↗</a>
                        {p.video && <a className="pp-act alt" href={videoUrl(p.video)} target="_blank" rel="noreferrer">▶ NeetCode's video</a>}
                    </div>

                    <div className="pp-card">
                        <h3><span>LOG IT</span>{previews === null && <span>schedules no review</span>}</h3>
                        <div className="pp-log">
                            {TILES.map((g) => (
                                <button key={g.grade} className={`lg ${g.cls}${s.last_grade === g.grade ? " on" : ""}`} disabled={busy} onClick={() => log(p, g.grade)}>
                                    <b>{g.glyph}</b><span>{g.label}</span><small>{gradeNote(g.grade)}</small>
                                </button>
                            ))}
                        </div>
                        <div className="pp-status">
                            <div className="pp-gauge" style={{ "--p": `${recall ?? 0}%` } as CSSProperties}><span>{recall != null ? `${recall}%` : "–"}</span></div>
                            <div><b>{standing[0]}</b><small>{standing[1]}{s.last_grade && recall != null && status !== "due" ? ` · ${recall}% recall now` : ""}</small></div>
                        </div>
                    </div>

                    {sameIdea.length > 1 && (
                        <div className="pp-card">
                            <h3><span>SAME IDEA</span><span>{sameIdea.length} problems</span></h3>
                            <div className="pp-rel">
                                {(more ? sameIdea : sameIdea.slice(0, SAME_IDEA_SHOWN)).map((x) => (
                                    <Link key={x.id} to="/d/$slug" params={{ slug: x.slug }} className={x.id === p.id ? "now" : ""}>
                                        <i className={dotOf(x)} />
                                        <span>{x.title}</span>
                                        <small>{x.id === p.id ? "THIS" : x.role === "must_learn" ? "MUST" : DIFF[x.difficulty][0][0]}</small>
                                    </Link>
                                ))}
                            </div>
                            {sameIdea.length > SAME_IDEA_SHOWN && (
                                <button className="pp-more" onClick={() => setMore(!more)}>{more ? "show fewer" : `+${sameIdea.length - SAME_IDEA_SHOWN} more`}</button>
                            )}
                        </div>
                    )}

                    {p.companies.length > 0 && (
                        <div className="pp-card">
                            <h3><span>ASKED AT</span><span>highlighted: last six months</span></h3>
                            <Companies companies={p.companies} limit={10} />
                        </div>
                    )}
                </aside>
            </div>
        </>,
    );
}
