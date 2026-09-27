import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api, type Band, type StageView } from "../api";
import { Header } from "../components/Header";
import { BAND_LABEL, ModeTag, Phase, Sech, Segs, StatusBox, pad2, progressLabel } from "../components/bits";
import { NAV_SECTIONS, SECTION_NAMES, type NavArea } from "../curriculum";

const BANDS: Band[] = ["easy", "medium", "hard"];
const TIER = { core: "CORE", light: "LIGHT", sde3: "SDE-3" } as const;

function stageKind(s: StageView, isCurrent: boolean) {
  if (s.total > 0 && s.solved === s.total) return "done" as const;
  if (isCurrent) return "cur" as const;
  return s.solved > 0 ? ("open" as const) : ("ahead" as const);
}

export function TrackPage({ slug }: { slug: string }) {
  const q = useQuery({ queryKey: ["track", slug], queryFn: () => api.track(slug) });
  const [stage, setStage] = useState<string | null>(null);
  const [tag, setTag] = useState<string | null>(null);
  const t = q.data;
  const area = t ? ((Object.keys(NAV_SECTIONS) as NavArea[]).find((a) => (NAV_SECTIONS[a] as readonly string[]).includes(t.section)) ?? "dsa") : undefined;

  if (!t) {
    return (
      <>
        <Header />
        <main className="page">
          <div className="wrap">
            <p className="notice">{q.isError ? `Couldn't load track ${slug}.` : "Loading…"}</p>
          </div>
        </main>
      </>
    );
  }

  // The stage you're on: the first with something written and unsolved; otherwise the first unfinished one.
  const workable = t.stages.findIndex((s) => s.ready > 0 && s.solved < s.total);
  const current = workable >= 0 ? workable : t.stages.findIndex((s) => s.solved < s.total);
  const selected = stage ?? null;
  const rows = t.problems.filter((p) => (!selected || p.stage === selected) && (!tag || p.tags.includes(tag)));
  const tags = [...new Set(t.problems.filter((p) => !selected || p.stage === selected).flatMap((p) => p.tags))];
  const nextUp = t.problems.find((p) => p.status === "ready" && p.progress !== "solved" && p.progress !== "assisted");
  const cols = "40px 52px minmax(0,1.5fr) 100px 90px minmax(0,1.1fr) 110px";

  return (
    <>
      <Header area={area} />
      <main className="page">
        <div className="wrap">
          <section className="hero solo">
            <div>
              <div className="eyebrow">
                <span style={{ color: "var(--acc)" }}>{t.code}</span>
                <span>/</span>
                <span>{SECTION_NAMES[t.section].toUpperCase()}</span>
                <span>/</span>
                <span>{TIER[t.tier]}</span>
              </div>
              <h1 className="h1 md">{t.name}</h1>
              {t.summary && <p className="lead">{t.summary}</p>}
              {nextUp && (
                <div className="btns">
                  <Link className="btn go" to="/p/$id" params={{ id: nextUp.id }}>
                    {nextUp.progress === "started" ? "Resume" : "Start"} · {nextUp.title} →
                  </Link>
                </div>
              )}
            </div>
          </section>
          <section className="strip">
            <div>
              <span className="k">SOLVED</span>
              <span className="v" style={{ color: "var(--grn)" }}>
                {t.solved} of {t.total}
              </span>
              <span className="s">{t.ready} ready to solve</span>
            </div>
            <div>
              <span className="k">NOW ON</span>
              <span className="v" style={{ color: "var(--acc)" }}>
                {t.stages[current]?.name ?? "Done"}
              </span>
              <span className="s">{current >= 0 ? `stage ${current + 1} of ${t.stages.length}` : "every stage solved"}</span>
            </div>
            <div>
              <span className="k">STAGES</span>
              <span className="v">{t.stages.length}</span>
              <span className="s">easy → medium → hard</span>
            </div>
            <div>
              <span className="k">NEXT UP</span>
              <span className="v" style={{ fontSize: 18 }}>
                {nextUp?.title ?? "—"}
              </span>
              <span className="s">{nextUp ? `${nextUp.level} · ${nextUp.mode === "fix" ? "fix this" : "write it"}` : "nothing ready yet"}</span>
            </div>
          </section>

          <section className="sec" style={{ paddingTop: 56 }}>
            <Sech title="THE STAGES" caption="click a stage to filter the problems" />
            <div className="bandcols">
              {BANDS.map((b) => {
                const list = t.stages.map((s, i) => [s, i] as const).filter(([s]) => s.band === b);
                return (
                  <div className="bandcol" key={b}>
                    <div className="bandh">
                      <span>{BAND_LABEL[b]}</span>
                      <span>{list.length} stages</span>
                    </div>
                    {list.map(([s, i]) => {
                      const kind = stageKind(s, i === current);
                      const label =
                        kind === "done" ? `SOLVED · ${s.solved}/${s.total}` : kind === "cur" ? `IN PROGRESS · ${s.solved}/${s.total}` : kind === "open" ? `OPEN · ${s.solved}/${s.total}` : `AHEAD · ${s.total}`;
                      const on = selected === s.slug;
                      return (
                        <button
                          key={s.slug}
                          className={`scard${on ? " sel" : ""}`}
                          aria-pressed={on}
                          onClick={() => {
                            setStage(on ? null : s.slug);
                            setTag(null);
                          }}
                        >
                          <span className="sn">
                            <span>{s.name}</span>
                            <span className="m" style={{ fontSize: 10, color: "var(--dim)" }}>
                              {pad2(i + 1)}
                            </span>
                          </span>
                          <Phase kind={kind}>{label}</Phase>
                          <Segs n={s.total} filled={s.solved} color={kind === "ahead" ? "var(--line2)" : "var(--grn)"} />
                          <span className="m" style={{ fontSize: 10.5, color: "var(--dim)" }}>
                            {s.ready} of {s.total} written
                          </span>
                        </button>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </section>

          <section className="sec" style={{ paddingTop: 48 }}>
            <Sech
              title={selected ? `STAGE · ${t.stages.find((s) => s.slug === selected)?.name.toUpperCase()}` : "ALL PROBLEMS"}
              caption={`${rows.length} problems · ${rows.filter((p) => p.mode === "fix").length} fix-this`}
            />
            <div className="chips" hidden={!selected}>
              {[null, ...tags].map((x) => (
                <button key={x ?? "all"} className={`chip${tag === x ? " on" : ""}`} onClick={() => setTag(x)}>
                  {x ?? "all"}
                </button>
              ))}
            </div>
            <div className="tblw">
              <div className="tbl">
                <div className="tr th" style={{ gridTemplateColumns: cols }}>
                  <span />
                  <span>#</span>
                  <span>PROBLEM</span>
                  <span>MODE</span>
                  <span>LEVEL</span>
                  <span>TAGS</span>
                  <span style={{ textAlign: "right" }}>STATUS</span>
                </div>
                {rows.map((p) => {
                  const cells = (
                    <>
                      <StatusBox progress={p.progress} />
                      <span className="num">{pad2(p.order)}</span>
                      <span className="pt">{p.title}</span>
                      <span>
                        <ModeTag mode={p.mode} />
                      </span>
                      <span className="lvl">{p.level}</span>
                      <span className="tags">{p.tags.join(" · ")}</span>
                      <span className="best" style={{ color: p.status === "draft" ? "var(--dim)" : p.progress === "not_started" ? "var(--mut)" : "var(--grn)" }}>
                        {p.status === "draft" ? "not written" : progressLabel(p.progress)}
                      </span>
                    </>
                  );
                  return p.status === "ready" ? (
                    <Link key={p.id} className={`tr${p.progress === "started" ? " cur" : ""}`} to="/p/$id" params={{ id: p.id }} style={{ gridTemplateColumns: cols }}>
                      {cells}
                    </Link>
                  ) : (
                    <div key={p.id} className="tr tr-draft" style={{ gridTemplateColumns: cols }}>
                      {cells}
                    </div>
                  );
                })}
              </div>
            </div>
          </section>
        </div>
      </main>
    </>
  );
}
