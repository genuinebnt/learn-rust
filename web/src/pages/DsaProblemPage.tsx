import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import type { CSSProperties } from "react";
import { api } from "../api";
import { Companies, Mark, useLogger } from "../components/dsaBits";
import { Header } from "../components/Header";
import { DIFF, GRADES, MINUTES, leetcode, niceDate, statusOf, videoUrl } from "../dsa";

/** A NeetCode problem: where to solve it, what idea it belongs to, and the log buttons. The written lesson comes later. */
export function DsaProblemPage({ slug }: { slug: string }) {
  const overview = useQuery({ queryKey: ["dsa"], queryFn: api.dsa });
  const o = overview.data;
  const { log, toast } = useLogger(o?.today);
  const p = o?.problems.find((x) => x.slug === slug);
  const frame = (body: React.ReactNode) => (
    <>
      <Header area="dsa" />
      <main className="page" style={{ "--ca": "var(--acc)", "--cab": "var(--acc-bg)" } as CSSProperties}>
        <div className="wrap" style={{ maxWidth: 860, paddingBlock: 32 }}>
          {body}
        </div>
      </main>
      {toast}
    </>
  );
  if (!o) return frame(<p className="rempty">{overview.isError ? "Couldn't reach the API." : "Loading…"}</p>);
  if (!p) return frame(<p className="notice bad">No NeetCode problem called {slug}. <Link to="/dsa">Back to the list</Link></p>);

  const pattern = o.patterns.find((x) => x.code === p.pattern);
  const technique = o.techniques.find((t) => t.id === p.technique);
  const teacher = p.practice_of ? o.problems.find((x) => x.id === p.practice_of) : undefined;
  const mustLearn = technique ? o.problems.find((x) => x.id === technique.must_learn) : undefined;
  const practice = o.problems.filter((x) => x.practice_of === p.id);
  const status = statusOf(p, o.today);
  const s = p.state;
  return frame(
    <>
      <div className="eyebrow">
        <Link to="/dsa" style={{ color: "var(--ca)" }}>DSA</Link>
        <span>/</span>
        <span>{pattern?.name.toUpperCase()}</span>
        <span>/</span>
        <span>#{p.number}</span>
      </div>
      <h1 className="h1 md" style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <Mark p={p} today={o.today} />
        {p.title}
      </h1>
      <div className="d-pmeta" style={{ margin: "10px 0 18px" }}>
        <span className="d-lv" style={{ color: DIFF[p.difficulty][1] }}>{DIFF[p.difficulty][0]}</span>
        {p.role === "must_learn" ? <span className="d-bdg ml">MUST LEARN</span> : <span className="d-bdg">PRACTICE</span>}
        {p.premium && <span className="d-bdg prem">PREMIUM</span>}
        <span>~{MINUTES[p.difficulty]}m</span>
        <span>{p.tags.join(" · ")}</span>
      </div>
      <div className="d-acts" style={{ justifyContent: "flex-start", gap: 10, marginBottom: 22 }}>
        <a className="nu-go" style={{ display: "inline-flex" }} href={leetcode(p.slug)} target="_blank" rel="noreferrer">Solve on LeetCode ↗</a>
        {p.video && <a href={videoUrl(p.video)} target="_blank" rel="noreferrer" style={{ height: 38, padding: "0 14px" }}>▶ NeetCode's video</a>}
      </div>

      <section className="rbox" style={{ marginBottom: 18 }}>
        <h4><span>LOG IT</span><span style={{ color: "var(--dim)" }}>{s.last_grade ? `${s.reps} log${s.reps === 1 ? "" : "s"} · ${s.lapses} lapse${s.lapses === 1 ? "" : "s"}` : "not logged yet"}</span></h4>
        <div className="d-acts" style={{ justifyContent: "flex-start", gap: 10 }}>
          {GRADES.map((g) => (
            <button key={g.grade} className={g.cls} style={{ height: 36, padding: "0 14px" }} onClick={() => log(p, g.grade)}>
              {g.glyph} {g.label}
            </button>
          ))}
          <button style={{ height: 36, padding: "0 14px" }} onClick={() => log(p, "easy")}>⚡ Instant</button>
        </div>
        <p className="rempty" style={{ marginTop: 10 }}>
          {s.due
            ? status === "due"
              ? `Review due ${s.due < o.today ? "now" : "today"}.`
              : s.last_grade === "again"
                ? `Retry ${niceDate(s.due, o.today)}.`
                : `Next review ${niceDate(s.due, o.today)}${s.retrievability != null ? ` · ${Math.round(s.retrievability * 100)}% recall now` : ""}.`
            : "Solve it on LeetCode, then log how it went. The next review is scheduled for you."}
        </p>
      </section>

      <section className="rbox" style={{ marginBottom: 18 }}>
        <h4><span>THE IDEA</span></h4>
        {technique ? (
          <p style={{ margin: 0 }}>
            <b>{technique.name}</b>.{" "}
            {p.role === "must_learn" ? "This is the problem that teaches it first." : teacher ? <>Practice for <Link to="/d/$slug" params={{ slug: teacher.slug }} style={{ color: "var(--ca)" }}>{teacher.title}</Link>, which teaches it.</> : null}
            {" "}{technique.problems} problem{technique.problems === 1 ? "" : "s"} use it.
          </p>
        ) : null}
        {mustLearn && mustLearn.id !== p.id && !teacher && (
          <Link to="/d/$slug" params={{ slug: mustLearn.slug }} style={{ color: "var(--ca)" }}>{mustLearn.title}</Link>
        )}
        {practice.length > 0 && (
          <div className="d-prac" style={{ gridColumn: "auto", marginTop: 12 }}>
            <span>PRACTICE THIS IDEA · {practice.length}</span>
            {practice.map((c) => (
              <Link key={c.id} className="d-pp" to="/d/$slug" params={{ slug: c.slug }}>
                <i className={c.state.last_grade ? (c.state.last_grade === "again" ? "fail" : c.state.last_grade === "hard" ? "help" : "solo") : ""} />
                {c.title}
                <small style={{ color: DIFF[c.difficulty][1] }}>{DIFF[c.difficulty][0][0]}</small>
              </Link>
            ))}
          </div>
        )}
      </section>

      {p.companies.length > 0 && (
        <section className="rbox" style={{ marginBottom: 18 }}>
          <h4><span>ASKED AT</span><span style={{ color: "var(--dim)" }}>highlighted: last six months</span></h4>
          <Companies companies={p.companies} limit={40} />
        </section>
      )}
      <p className="rempty">Part of: {p.lists.map((l) => ({ blind75: "Blind 75", neetcode150: "NeetCode 150", neetcode250: "NeetCode 250", all: "NeetCode All" })[l]).join(", ")}.</p>
    </>,
  );
}
