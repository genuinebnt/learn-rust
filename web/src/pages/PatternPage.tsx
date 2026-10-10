import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type PatternExtra, type PatternLessons, type PatternListed, type PatternTechnique, type TechniqueLesson } from "../api";
import { ProblemLine, PyCode } from "../components/dsaBits";
import { PatternShell } from "../components/PatternShell";

/** A pattern's Learn page (docs/DSA_LEARN_PAGE_SPEC.md). Each technique is a card: its implementation on the left (when to use it, the
 *  Python template, the traps), the LeetCode problems that practise it on the right, whether or not they are in a NeetCode list.
 *  Techniques that have no problem are only named, at the bottom. */
export function PatternPage({ code }: { code: string }) {
  const overview = useQuery({ queryKey: ["dsa"], queryFn: api.dsa });
  const lessons = useQuery({ queryKey: ["patterns", code], queryFn: () => api.patternLessons(code) });
  const today = overview.data?.today ?? "";
  const d = lessons.data;
  return (
    <PatternShell code={code} tab="learn">
      {lessons.isError && <p className="notice bad">Couldn't load the lessons: {(lessons.error as Error).message}</p>}
      {d && (
        <>
          {d.groups ? <Grouped d={d} today={today} /> : <Flat d={d} today={today} />}
          <OtherTechniques items={d.listed ?? []} />
        </>
      )}
    </PatternShell>
  );
}

const anchor = (id: string) => `t-${id.split(":")[1] ?? id}`;

/** A page whose techniques have no groups: the jump list, then the cards. */
function Flat({ d, today }: { d: PatternLessons; today: string }) {
  return (
    <>
      <nav className="l-jump" aria-label="Techniques">
        {d.techniques.map((t) => (
          <a key={t.id} href={`#${anchor(t.id)}`}>{t.name}</a>
        ))}
      </nav>
      {d.techniques.map((t) => (
        <Technique key={t.id} t={t} today={today} />
      ))}
    </>
  );
}

/** A page whose techniques are sorted into sections. A section is a heading: it holds cards and nothing else. */
function Grouped({ d, today }: { d: PatternLessons; today: string }) {
  const groups = d.groups ?? [];
  const inGroup = (g: string) => ({
    techniques: d.techniques.filter((t) => t.lesson?.group === g),
    extras: d.extras.filter((e) => e.group === g),
  });
  // a technique of the lists that no section claims sits first, under its own heading
  const ungrouped = d.techniques.filter((t) => !t.lesson?.group || !groups.includes(t.lesson.group));
  return (
    <>
      <nav className="l-jumpg" aria-label="Techniques by section">
        {groups.map((g) => {
          const x = inGroup(g);
          if (x.techniques.length + x.extras.length === 0) return null;
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
              </div>
            </div>
          );
        })}
      </nav>
      {ungrouped.length > 0 && (
        <section className="l-gsec">
          <div className="l-grp"><h2>More</h2><small>{ungrouped.length} techniques</small></div>
          {ungrouped.map((t) => <Technique key={t.id} t={t} today={today} />)}
        </section>
      )}
      {groups.map((g) => {
        const x = inGroup(g);
        const n = x.techniques.length + x.extras.length;
        if (n === 0) return null;
        return (
          <section key={g} aria-label={g} className="l-gsec">
            <div className="l-grp">
              <h2>{g}</h2>
              <small>{n} technique{n === 1 ? "" : "s"}</small>
            </div>
            {x.techniques.map((t) => <Technique key={t.id} t={t} today={today} />)}
            {x.extras.map((e) => <Extra key={e.id} e={e} today={today} />)}
          </section>
        );
      })}
    </>
  );
}

/** Techniques of this topic that have no problem attached (or no implementation yet): named, nothing more. */
function OtherTechniques({ items }: { items: PatternListed[] }) {
  const [open, setOpen] = useState(false);
  if (items.length === 0) return null;
  return (
    <section className="l-other" aria-label="Other techniques">
      <button className="l-ltoggle" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span aria-hidden="true">{open ? "▾" : "▸"}</span>
        Other techniques of this topic ({items.length})
        <small> · no LeetCode problem is attached to them here</small>
      </button>
      {open && (
        <ul className="l-onames">
          {items.map((l) => (
            <li key={`${l.group}:${l.name}`}>{l.name}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

/** The template, with a tab for each variant (recursive and iterative DFS). */
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

/** The left of a card: when to use it, the implementation, the traps. */
function Implementation({ lesson }: { lesson: TechniqueLesson }) {
  return (
    <>
      <span className="l-lab">USE IT WHEN</span>
      <div className="l-when">
        {lesson.signals.map((s) => <span key={s}>{s}</span>)}
      </div>
      <Templates lesson={lesson} />
      <span className="l-lab">TRAPS</span>
      <ul className="l-pit">{lesson.pitfalls.map((p) => <li key={p}>{p}</li>)}</ul>
    </>
  );
}

/** A technique of the NeetCode lists: its implementation, and every problem that practises it (list or not). */
function Technique({ t, today }: { t: PatternTechnique; today: string }) {
  const lists = t.problems.filter((p) => p.list_tag).length;
  return (
    <article className="l-pat" id={anchor(t.id)}>
      <div className="l-lft">
        <h3>
          {t.name}
          <small>{t.solved} / {lists} in the lists</small>
        </h3>
        {t.lesson ? <Implementation lesson={t.lesson} /> : <p className="l-soon">The implementation isn't written yet.</p>}
      </div>
      <div className="l-rgt">
        <span className="l-lab">PROBLEMS · {t.problems.length}</span>
        <div className="l-plist">
          {t.problems.map((p) => <ProblemLine key={p.id} p={p} today={today} />)}
        </div>
      </div>
    </article>
  );
}

/** A technique that no NeetCode problem teaches first: the same card, its problems on the right. */
function Extra({ e, today }: { e: PatternExtra; today: string }) {
  return (
    <article className="l-pat" id={anchor(e.id)}>
      <div className="l-lft">
        <h3>
          {e.name}
          {(e.lesson.variant?.length ?? 0) > 0 && <span className="l-tag var">{(e.lesson.variant?.length ?? 0) + 1} VERSIONS</span>}
        </h3>
        <Implementation lesson={e.lesson} />
      </div>
      <div className="l-rgt">
        <span className="l-lab">PROBLEMS · {e.examples.length}</span>
        <div className="l-plist">
          {e.examples.map((p) => <ProblemLine key={p.id} p={p} today={today} />)}
        </div>
      </div>
    </article>
  );
}
