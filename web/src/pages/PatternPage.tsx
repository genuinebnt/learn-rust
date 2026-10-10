import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api, type ExternalProblem, type PatternExtra, type PatternLessons, type PatternListed, type PatternTechnique, type TechniqueLesson } from "../api";
import { Mark, PyCode } from "../components/dsaBits";
import { PatternShell } from "../components/PatternShell";
import { DIFF } from "../dsa";

/** A pattern's lessons: for each technique, the signals that call for it, a template, the traps, and its problems. */
export function PatternPage({ code }: { code: string }) {
  const overview = useQuery({ queryKey: ["dsa"], queryFn: api.dsa });
  const lessons = useQuery({ queryKey: ["patterns", code], queryFn: () => api.patternLessons(code) });
  const today = overview.data?.today ?? "";
  const d = lessons.data;
  const written = d?.techniques.filter((t) => t.lesson).length ?? 0;
  return (
    <PatternShell code={code} tab="learn">
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
              {d.groups ? (
                <Grouped d={d} today={today} />
              ) : (
                <>
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
            </>
          )}
    </PatternShell>
  );
}

const anchor = (id: string) => `t-${id.split(":")[1] ?? id}`;

/** A page whose techniques are sorted into groups (decision 32): a jump list by group, then each group's cards. */
function Grouped({ d, today }: { d: PatternLessons; today: string }) {
  const groups = d.groups ?? [];
  const listed = d.listed ?? [];
  const inGroup = (g: string) => ({
    techniques: d.techniques.filter((t) => t.lesson?.group === g),
    extras: d.extras.filter((e) => e.group === g),
    listed: listed.filter((l) => l.group === g),
  });
  // A technique without a lesson has no group yet: it sits first, under its own heading.
  const ungrouped = d.techniques.filter((t) => !t.lesson?.group);
  return (
    <>
      <nav className="l-jumpg" aria-label="Techniques by group">
        {groups.map((g) => {
          const x = inGroup(g);
          if (x.techniques.length + x.extras.length + x.listed.length === 0) return null;
          return (
            <div className="l-jg" key={g}>
              <span>{g.toUpperCase()}</span>
              <div className="l-chips">
                {x.techniques.map((t) => (
                  <a key={t.id} href={`#${anchor(t.id)}`}><i />{t.name}</a>
                ))}
                {x.extras.map((e) => (
                  <a key={e.id} href={`#${anchor(e.id)}`} className="ex"><i />{e.name}</a>
                ))}
                {x.techniques.length + x.extras.length === 0 && <span className="l-nolesson">{x.listed.length} listed, no lesson written yet</span>}
              </div>
            </div>
          );
        })}
      </nav>
      {ungrouped.length > 0 && (
        <>
          <div className="l-grp"><h2>More</h2><small>{ungrouped.length} techniques</small></div>
          {ungrouped.map((t) => <Technique key={t.id} t={t} today={today} code={d.code} />)}
        </>
      )}
      {groups.map((g) => {
        const x = inGroup(g);
        const n = x.techniques.length + x.extras.length;
        if (n + x.listed.length === 0) return null;
        return (
          <section key={g} aria-label={g} className="l-gsec">
            <div className="l-grp">
              <h2>{g}</h2>
              <small>{n} written{x.listed.length > 0 ? ` · ${x.listed.length} listed` : ""}</small>
              {(d.group_tags?.[g] ?? []).length > 0 && (
                <span className="l-tags">
                  on LeetCode:{" "}
                  {(d.group_tags?.[g] ?? []).map((t) => (
                    <a key={t} href={`https://leetcode.com/tag/${t}/`} target="_blank" rel="noreferrer">{tagName(t)} ↗</a>
                  ))}
                </span>
              )}
            </div>
            {x.techniques.map((t) => <Technique key={t.id} t={t} today={today} code={d.code} />)}
            {x.extras.map((e) => <Extra key={e.id} e={e} today={today} />)}
            {(d.group_problems?.[g]?.length ?? 0) > 0 && <MoreProblems problems={d.group_problems?.[g] ?? []} />}
            {x.listed.length > 0 && <Listed items={x.listed} />}
          </section>
        );
      })}
    </>
  );
}

/** More LeetCode problems for a group: they carry one of the group's LeetCode topic tags and are not in your lists. They link out. */
function MoreProblems({ problems }: { problems: ExternalProblem[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="l-listed">
      <button className="l-ltoggle" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span aria-hidden="true">{open ? "▾" : "▸"}</span>
        {problems.length} more LeetCode problems for this section
        <small> · not in your lists, not tracked here</small>
      </button>
      {open && (
        <div className="l-plist">
          {problems.map((p) => (
            <a key={p.slug} className="l-prow" href={`https://leetcode.com/problems/${p.slug}/`} target="_blank" rel="noreferrer">
              <span className="l-pt">#{p.number} {p.title}</span>
              {p.premium && <span className="d-bdg prem">PREM</span>}
              <span className="d-lv" style={{ color: DIFF[p.difficulty][1] }}>{DIFF[p.difficulty][0]}</span>
              <span aria-hidden="true">↗</span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

const tagName = (slug: string) => slug.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");

/** Techniques that are known and not written yet. Collapsed: a chip with problems opens them, with a link to LeetCode for each. */
function Listed({ items }: { items: PatternListed[] }) {
  const [open, setOpen] = useState(false);
  const [sel, setSel] = useState<string | null>(null);
  const withProblems = items.filter((l) => (l.problems?.length ?? 0) > 0).length;
  const chosen = items.find((l) => l.name === sel);
  return (
    <div className="l-listed">
      <button className="l-ltoggle" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span aria-hidden="true">{open ? "▾" : "▸"}</span>
        {items.length} more technique{items.length === 1 ? "" : "s"} listed, no lesson yet
        {withProblems > 0 && <small> · {withProblems} with LeetCode problems</small>}
      </button>
      {open && (
        <>
          <div className="l-chips">
            {items.map((l) => (
              <button key={l.name} title={l.name} className={`l-lchip${l.problems?.length ? " has" : ""}${sel === l.name ? " on" : ""}`} aria-pressed={sel === l.name} onClick={() => setSel(sel === l.name ? null : l.name)}>
                {l.name}
                {l.problems?.length ? <sup>{l.problems.length}</sup> : null}
              </button>
            ))}
          </div>
          {chosen && (
            <div className="l-lpanel">
              {chosen.note && <p>{chosen.note}</p>}
              {(chosen.problems?.length ?? 0) > 0 ? (
                <div className="l-plist">
                  {chosen.problems!.map((p: ExternalProblem) => (
                    <a key={p.slug} className="l-prow" href={`https://leetcode.com/problems/${p.slug}/`} target="_blank" rel="noreferrer">
                      <span className="l-pt">#{p.number} {p.title}</span>
                      {p.premium && <span className="d-bdg prem">PREM</span>}
                      <span className="d-lv" style={{ color: DIFF[p.difficulty][1] }}>{DIFF[p.difficulty][0]}</span>
                      <span aria-hidden="true">↗</span>
                    </a>
                  ))}
                  <p className="l-lnote">On LeetCode, outside your lists: not tracked here.</p>
                </div>
              ) : (
                <p className="l-lnote">No LeetCode problem is attached to this one yet.</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

/** The template, with a tab for each variant (recursive and iterative DFS). The tab is remembered while you read the page. */
function Templates({ lesson }: { lesson: TechniqueLesson }) {
  const variants = lesson.variant ?? [];
  const [i, setI] = useState(0);
  if (variants.length === 0) {
    return (
      <>
        <span className="l-lab">TEMPLATE · PYTHON</span>
        <PyCode code={lesson.template.trim()} />
      </>
    );
  }
  const first = { name: lesson.template_name ?? "Template", note: "", template: lesson.template };
  const tabs = [first, ...variants];
  const cur = tabs[i] ?? first;
  return (
    <>
      <span className="l-lab">TEMPLATE · PYTHON</span>
      <div className="l-tabs" role="tablist" aria-label="Versions of the template">
        {tabs.map((t, k) => (
          <button key={t.name} role="tab" aria-selected={k === i} onClick={() => setI(k)}>{t.name.toUpperCase()}</button>
        ))}
      </div>
      {cur.note && <p className="l-tabnote">{cur.note}</p>}
      <PyCode code={cur.template.trim()} />
    </>
  );
}

/** A lesson for a technique that has no must-learn problem in the lists, taught with example problems. */
function Extra({ e, today }: { e: PatternExtra; today: string }) {
  return (
    <article className="l-pat" id={anchor(e.id)}>
      <div className="l-lft">
        <h3>
          {e.name}
          <span className="l-tag ex">EXAMPLES</span>
          {(e.lesson.variant?.length ?? 0) > 0 && <span className="l-tag var">{(e.lesson.variant?.length ?? 0) + 1} VERSIONS</span>}
        </h3>
        <span className="l-lab">USE IT WHEN</span>
        <div className="l-when">
          {e.lesson.signals.map((x) => <span key={x}>{x}</span>)}
        </div>
        <Templates lesson={e.lesson} />
      </div>
      <div className="l-rgt">
        <span className="l-lab">PITFALLS</span>
        <ul className="l-pit">{e.lesson.pitfalls.map((p) => <li key={p}>{p}</li>)}</ul>
        <p className="l-exnote">
          <b>No must-learn problem of your lists belongs here.</b> These problems from the lists use the idea; they are examples, not the first problem that teaches it.
        </p>
        <span className="l-lab">EXAMPLES</span>
        <div className="l-plist">
          {e.examples.map((p) => (
            <Link key={p.id} to="/d/$slug" params={{ slug: p.slug }} className="l-prow">
              <Mark p={p} today={today} />
              <span className="l-pt">{p.title}</span>
              <span className="d-bdg ex">EXAMPLE</span>
              {p.premium && <span className="d-bdg prem">PREM</span>}
              <span className="d-lv" style={{ color: DIFF[p.difficulty][1] }}>{DIFF[p.difficulty][0]}</span>
            </Link>
          ))}
        </div>
      </div>
    </article>
  );
}

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
            <Templates lesson={t.lesson} />
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
