import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import type { CSSProperties } from "react";
import { api, type PatternTechnique } from "../api";
import { Mark, PyCode } from "../components/dsaBits";
import { Header } from "../components/Header";
import { DIFF } from "../dsa";

/** A pattern's lessons: for each technique, the signals that call for it, a template, the traps, and its problems. */
export function PatternPage({ code }: { code: string }) {
  const overview = useQuery({ queryKey: ["dsa"], queryFn: api.dsa });
  const lessons = useQuery({ queryKey: ["patterns", code], queryFn: () => api.patternLessons(code) });
  const today = overview.data?.today ?? "";
  const pattern = overview.data?.patterns.find((p) => p.code.toLowerCase() === code.toLowerCase() || p.slug === code);
  const d = lessons.data;
  const written = d?.techniques.filter((t) => t.lesson).length ?? 0;
  return (
    <>
      <Header area="dsa" />
      <main className="page" style={{ "--ca": "var(--acc)", "--cab": "var(--acc-bg)" } as CSSProperties}>
        <div className="wrap" style={{ paddingBlock: 28, display: "flex", flexDirection: "column", gap: 18 }}>
          <div className="eyebrow">
            <Link to="/dsa" style={{ color: "var(--ca)" }}>DSA</Link>
            <span>/</span>
            <span>PATTERNS</span>
            <span>/</span>
            <span>{(d?.pattern ?? pattern?.name ?? code).toUpperCase()}</span>
          </div>
          <h1 className="h1 md">{d?.pattern ?? pattern?.name ?? "Patterns"}</h1>
          <div className="d-ptabs" role="tablist">
            <Link to="/dsa" role="tab" aria-selected="false">
              Problems<small>{pattern?.total ?? ""}</small>
            </Link>
            <span role="tab" aria-selected="true" className="on">
              Patterns<small>{d ? `${d.techniques.length} techniques` : ""}</small>
            </span>
            {pattern && pattern.practice_total > 0 && (
              <Link to="/dsa/practice/$code" params={{ code: pattern.code }} role="tab" aria-selected="false">
                Practice<small>{pattern.practice_solved} / {pattern.practice_total} solved</small>
              </Link>
            )}
          </div>
          {lessons.isError && <p className="notice bad">Couldn't load the lessons: {(lessons.error as Error).message}</p>}
          {d && (
            <>
              <p className="l-intro">
                {d.intro ?? `${d.total} problems across the lists, grouped by the idea they use.`}
                {d.intro && <span> {d.total} problems in the lists, must-learn first in each group.</span>}
              </p>
              {written < d.techniques.length && (
                <p className="l-soon">{written === 0 ? "The lessons for this pattern aren't written yet; the groups below still show its problems." : `${written} of ${d.techniques.length} lessons written; the rest are coming.`}</p>
              )}
              <nav className="l-jump" aria-label="Techniques">
                {d.techniques.map((t) => (
                  <a key={t.id} href={`#${anchor(t.id)}`}>{t.name}</a>
                ))}
              </nav>
              {d.techniques.map((t) => (
                <Technique key={t.id} t={t} today={today} code={d.code} />
              ))}
            </>
          )}
        </div>
      </main>
    </>
  );
}

const anchor = (id: string) => `t-${id.split(":")[1] ?? id}`;

function Technique({ t, today, code }: { t: PatternTechnique; today: string; code: string }) {
  const total = t.problems.length;
  return (
    <article className="l-pat" id={anchor(t.id)}>
      <div className="l-lft">
        <h3>
          {t.name}
          <small>{t.solved} / {total}</small>
          <span className="l-pb"><i style={{ width: `${total ? (t.solved / total) * 100 : 0}%` }} /></span>
        </h3>
        {t.lesson ? (
          <>
            <span className="l-lab">USE IT WHEN</span>
            <div className="l-when">
              {t.lesson.signals.map((s) => <span key={s}>{s}</span>)}
            </div>
            <span className="l-lab">TEMPLATE · PYTHON</span>
            <PyCode code={t.lesson.template.trim()} />
          </>
        ) : (
          <p className="l-soon">The lesson for this technique isn't written yet. Its problems are on the right.</p>
        )}
      </div>
      <div className="l-rgt">
        {t.lesson && (
          <>
            <span className="l-lab">PITFALLS</span>
            <ul className="l-pit">{t.lesson.pitfalls.map((p) => <li key={p}>{p}</li>)}</ul>
          </>
        )}
        <span className="l-lab">PROBLEMS · MUST LEARN FIRST</span>
        <div className="l-plist">
          {t.problems.map((p) => (
            <Link key={p.id} to="/d/$slug" params={{ slug: p.slug }} className="l-prow">
              <Mark p={p} today={today} />
              <span className="l-pt">{p.title}</span>
              {p.role === "must_learn" && <span className="d-bdg ml">MUST</span>}
              {p.premium && <span className="d-bdg prem">PREM</span>}
              <span className="d-lv" style={{ color: DIFF[p.difficulty][1] }}>{DIFF[p.difficulty][0]}</span>
            </Link>
          ))}
        </div>
        {t.practice_total > 0 && (
          <Link to="/dsa/practice/$code" params={{ code }} className="l-more">
            {t.practice_total} more to practise this on LeetCode ({t.practice_solved} solved) ›
          </Link>
        )}
      </div>
    </article>
  );
}
