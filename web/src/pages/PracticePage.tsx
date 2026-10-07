import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import type { CSSProperties } from "react";
import { api, type PracticeProblem, type PracticeTrack } from "../api";
import { Md } from "../components/dsaBits";
import { Header } from "../components/Header";
import { pad2 } from "../components/bits";
import { DIFF, MINUTES } from "../dsa";

const LANGUAGE: Record<PracticeTrack["language"], string> = { python: "PYTHON", rust: "RUST" };

/** A pattern's practice tracks: handwritten problems that make the idea stick, opened by logging LeetCode problems. */
export function PracticePage({ code }: { code: string }) {
  const overview = useQuery({ queryKey: ["dsa"], queryFn: api.dsa });
  const practice = useQuery({ queryKey: ["practice", code], queryFn: () => api.practice(code) });
  const pattern = overview.data?.patterns.find((p) => p.code.toLowerCase() === code.toLowerCase() || p.slug === code);
  const tracks = practice.data ?? [];
  const all = tracks.flatMap((t) => t.problems);
  const solved = all.filter((p) => p.progress === "solved" || p.progress === "assisted").length;
  const open = all.filter((p) => p.open).length;
  return (
    <>
      <Header area="dsa" />
      <main className="page" style={{ "--ca": "var(--acc)", "--cab": "var(--acc-bg)" } as CSSProperties}>
        <div className="wrap" style={{ paddingBlock: 28, display: "flex", flexDirection: "column", gap: 18 }}>
          <div className="eyebrow">
            <Link to="/dsa" style={{ color: "var(--ca)" }}>
              DSA
            </Link>
            <span>/</span>
            <span>PATTERNS</span>
            <span>/</span>
            <span>{pattern?.name.toUpperCase() ?? code.toUpperCase()}</span>
          </div>
          <h1 className="h1 md">{pattern?.name ?? "Practice"}</h1>
          <div className="d-ptabs" role="tablist">
            <Link to="/dsa" role="tab" aria-selected="false">
              Problems<small>{pattern?.total ?? ""}</small>
            </Link>
            <span role="tab" aria-selected="true" className="on">
              Practice
              <small>
                {open} / {all.length} unlocked
              </small>
            </span>
          </div>
          {practice.isError && <p className="notice bad">Couldn't load the practice track: {(practice.error as Error).message}</p>}
          {practice.isSuccess && tracks.length === 0 && (
            <div className="d-note">
              <div>
                <b>No practice track for {pattern?.name ?? "this pattern"} yet.</b> They're written one pattern at a time: Graphs first, then dynamic programming, then the rest.
              </div>
            </div>
          )}
          {tracks.length > 0 && (
            <>
              <div className="d-note">
                <div>
                  <b>These are not LeetCode problems.</b> They are small problems written for anneal that use the same idea in a new setting, to make the pattern stick. Solve them here; the tests run in the sandbox. They never schedule reviews.
                </div>
              </div>
              <div className="d-sum2">
                <span>
                  <b>{solved}</b> of {all.length} solved
                </span>
                <span className="bar">
                  <i style={{ width: `${all.length ? (solved / all.length) * 100 : 0}%` }} />
                </span>
                <span>{all.length - open} locked</span>
              </div>
            </>
          )}
          {tracks.map((t) => (
            <section key={t.code} className="d-pgrid-wrap">
              {tracks.length > 1 && (
                <div className="flabel">
                  {t.name.toUpperCase()} · {LANGUAGE[t.language]}
                </div>
              )}
              <div className="d-pgrid">
                {t.problems.map((p, i) => (
                  <PracticeCard key={p.id} p={p} n={i + 1} language={t.language} />
                ))}
              </div>
            </section>
          ))}
        </div>
      </main>
    </>
  );
}

function PracticeCard({ p, n, language }: { p: PracticeProblem; n: number; language: PracticeTrack["language"] }) {
  const solved = p.progress === "solved" || p.progress === "assisted";
  const head = (
    <div className="top">
      <span className="n">{pad2(n)}</span>
      <span>PRACTICE</span>
      <span className="pill py">{LANGUAGE[language]}</span>
      {solved && <span className="pill ok">SOLVED</span>}
      {p.warmup && p.open && !p.logged.length && <span className="pill">WARM-UP</span>}
    </div>
  );
  const names = p.unlocked_by.map((u) => u.title).join(" or ");
  if (!p.open) {
    return (
      <div className="pc locked" aria-disabled="true">
        {head}
        <h3>{p.title}</h3>
        <p>
          <Md inline text={p.blurb} />
        </p>
        <div className="lock">
          <i aria-hidden="true">🔒</i>
          <span>
            Log <b>{names}</b> on LeetCode to unlock{p.warmup ? ", or it opens when it's next up" : ""}
          </span>
        </div>
      </div>
    );
  }
  return (
    <Link to="/p/$id" params={{ id: p.id }} className={`pc open${solved ? " done" : ""}`}>
      {head}
      <h3>{p.title}</h3>
      <p>
        <Md inline text={p.blurb} />
      </p>
      <div className="unl">
        <i aria-hidden="true">{p.logged.length ? "✓" : "▸"}</i>
        <span>{p.logged.length ? `unlocked by ${names}` : `warm-up for ${names}, which is coming up`}</span>
      </div>
      <div className="foot">
        <span className="lv" style={{ color: DIFF[p.level][1] }}>
          {p.level}
        </span>
        <span>~{MINUTES[p.level]}m</span>
      </div>
    </Link>
  );
}
