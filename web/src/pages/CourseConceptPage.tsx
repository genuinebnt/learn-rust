import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState, type CSSProperties } from "react";
import { api } from "../api";
import { Header } from "../components/Header";
import { handleCodeClick, renderMd } from "./courseMd";

/** A concept: a short article that teaches one idea a stage needs. */
export function CourseConceptPage({ course, id }: { course: string; id: string }) {
    const q = useQuery({ queryKey: ["course-concept", course, id], queryFn: () => api.courseConcept(course, id) });
    const [active, setActive] = useState("");
    const p = q.data;
    useEffect(() => {
        window.scrollTo({ top: 0 });
    }, [id]);
    useEffect(() => {
        if (!p) return;
        const ids = p.concept.sections.map((s) => `c-${s.id}`);
        const onScroll = () => {
            let cur = ids[0] ?? "";
            for (const i of ids) {
                const el = document.getElementById(i);
                if (el && el.getBoundingClientRect().top < 200) cur = i;
            }
            setActive(cur);
        };
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
        return () => window.removeEventListener("scroll", onScroll);
    }, [p]);
    const style = { "--ca": "var(--grn)", "--cab": "var(--grn-bg)" } as CSSProperties;
    if (q.isError || !p) {
        return (
            <>
                <Header area="courses" />
                <main className="page">
                    <div className="wrap">
                        <p className={q.isError ? "notice bad" : "notice"}>{q.isError ? `Couldn't load ${id}: ${(q.error as Error).message}` : "Loading…"}</p>
                    </div>
                </main>
            </>
        );
    }
    const first = p.used_in[0];
    return (
        <>
            <Header area="courses" />
            <div className="subbar cx-sub">
                <div className="crumb">
                    <Link to="/courses" style={{ color: "var(--grn)" }}>
                        COURSES
                    </Link>
                    <span>/</span>
                    <span>CONCEPT</span>
                </div>
                <div className="vr" />
                <span className="wtitle">{p.concept.title}</span>
                <div className="subpills">
                    <span className="pill solid" style={{ background: "var(--vio)" }}>
                        CONCEPT
                    </span>
                    <span className="pill">~{p.concept.minutes} MIN</span>
                </div>
            </div>
            <div className="cx cx-two" style={style}>
                <div className="cx-main">
                    <main className="cx-read">
                        <div className="cx-col">
                            <div className="eyebrow">
                                <span style={{ color: "var(--vio)" }}>CONCEPT</span>
                                <span>/</span>
                                <span>~{p.concept.minutes} MIN READ</span>
                                {first && (
                                    <>
                                        <span>/</span>
                                        <span>USED IN {first.id.toUpperCase()}</span>
                                    </>
                                )}
                            </div>
                            <h1 className="cx-h1">{p.concept.title}</h1>
                            <p className="cx-lead">{p.concept.summary}</p>
                            <div className="cx-prose" onClick={handleCodeClick}>
                                {p.concept.sections.map((s, i) => (
                                    <section key={s.id} id={`c-${s.id}`}>
                                        <div className="cx-part">
                                            <b>{String(i + 1).padStart(2, "0")}</b>
                                            {s.title.toUpperCase()}
                                        </div>
                                        <div dangerouslySetInnerHTML={{ __html: renderMd(s.md) }} />
                                    </section>
                                ))}
                            </div>
                            {p.used_in.length > 0 && (
                                <>
                                    <div className="cx-part" style={{ marginTop: 56 }}>
                                        <b>BACK TO WORK</b>
                                    </div>
                                    <div className="cx-reads">
                                        {p.used_in.map((s) => (
                                            <Link key={s.id} to="/courses/$course/$stage" params={{ course, stage: s.id }}>
                                                <small>
                                                    STAGE {s.rank} · {s.module.toUpperCase()}
                                                </small>
                                                {s.title}
                                            </Link>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>
                    </main>
                </div>
                <aside className="cx-toc">
                    <div>
                        <h4>IN THIS CONCEPT</h4>
                        {p.concept.sections.map((s) => (
                            <a
                                key={s.id}
                                href={`#c-${s.id}`}
                                className={active === `c-${s.id}` ? "on" : ""}
                                onClick={(e) => {
                                    e.preventDefault();
                                    document.getElementById(`c-${s.id}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
                                }}
                            >
                                {s.title}
                            </a>
                        ))}
                    </div>
                </aside>
            </div>
        </>
    );
}
