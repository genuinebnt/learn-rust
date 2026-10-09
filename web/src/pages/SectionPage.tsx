import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { marked } from "marked";
import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { api, type Activity, type Band, type NextUp, type ReviewItem, type Section, type Tier, type TrackSummary } from "../api";
import { Header } from "../components/Header";
import { LEVEL_COLOR, pad2, pctColor } from "../components/bits";
import { BLURB, DSA_ORDER, NAV_SECTIONS, PLANNED, SECTION_NAMES, type NavArea, sectionOf } from "../curriculum";
import { CountUp } from "../components/kit";

const COPY: Record<NavArea, { eyebrow: string; color: string; title: [string, string]; lead: ReactNode }> = {
  dsa: {
    eyebrow: "DSA",
    color: "acc",
    title: ["Fourteen tracks, ", "easy to hard."],
    lead: (
      <>
        Every track climbs easy → medium → hard, and every problem is solved the way Rust wants it: index-based graphs,{" "}
        <code>Option&lt;Box&lt;Node&gt;&gt;</code> lists, heaps with <code>Reverse&lt;T&gt;</code>.
      </>
    ),
  },
  rust: {
    eyebrow: "RUST",
    color: "vio",
    title: ["The Rust interviewers ", "actually probe."],
    lead: "Language, standard library, concurrency and systems. Each track climbs from using the API, to understanding why it behaves that way, to building a small version yourself.",
  },
};

const TIER: Record<Tier, string> = { core: "CORE", light: "LIGHT", sde3: "SDE-3" };
/** Rough minutes per problem, for "to finish" and next-up estimates. */
const MINUTES: Record<Band, number> = { easy: 12, medium: 25, hard: 45 };
const BAND_COLOR: Record<Band, string> = LEVEL_COLOR;
const MODE_LABEL = { write: ["write it", "var(--acc)"], fix: ["fix this", "var(--vio)"], stage: ["stage", "var(--grn)"] } as const;

type State = "cur" | "open" | "ahead" | "done" | "planned";

interface Row {
  code: string;
  name: string;
  tier: Tier;
  planned: number;
  n: number;
  live?: TrackSummary;
  state: State;
}

const FILTERS: [key: string, label: string, test: (r: Row) => boolean][] = [
  ["all", "all", () => true],
  ["progress", "in progress", (r) => r.state === "cur" || r.state === "open"],
  ["new", "not started", (r) => r.state === "ahead"],
  ["done", "done", (r) => r.state === "done"],
  ["core", "core", (r) => r.tier === "core"],
  ["sde3", "SDE-3", (r) => r.tier === "sde3"],
  ["planned", "planned", (r) => r.state === "planned"],
];

function stateOf(live: TrackSummary | undefined, current: string | undefined): State {
  if (!live || live.ready === 0) return "planned";
  if (live.solved >= live.ready) return "done";
  if (live.code === current) return "cur";
  return live.solved > 0 ? "open" : "ahead";
}

function minutesTotal(r: Row) {
  if (!r.live) return r.planned * MINUTES.medium;
  return r.live.stages.reduce((n, s) => n + s.total * MINUTES[s.band], 0);
}

function minutesLeft(r: Row) {
  if (!r.live) return r.planned * MINUTES.medium;
  return r.live.stages.reduce((n, s) => n + (s.total - s.solved) * MINUTES[s.band], 0);
}

const hours = (m: number) => (m >= 600 ? `~${Math.round(m / 60)}h` : `~${(m / 60).toFixed(1).replace(/\.0$/, "")}h`);

function useStored<T extends string>(key: string, initial: T): [T, (v: T) => void] {
  const [v, set] = useState<T>(() => {
    try {
      return (localStorage.getItem(key) as T | null) ?? initial;
    } catch {
      return initial;
    }
  });
  return [
    v,
    (next) => {
      set(next);
      try {
        localStorage.setItem(key, next);
      } catch {
        // Storage can be unavailable; the choice still applies for this visit.
      }
    },
  ];
}

function BandBar({ row }: { row: Row }) {
  const bands = (["easy", "medium", "hard"] as const)
    .map((b) => {
      const ss = row.live?.stages.filter((s) => s.band === b) ?? [];
      return { b, total: ss.reduce((n, s) => n + s.total, 0), solved: ss.reduce((n, s) => n + s.solved, 0) };
    })
    .filter((x) => x.total > 0);
  if (!bands.length) return <div className="tc-bar"><span style={{ flex: 1 }} /></div>;
  return (
    <div className="tc-bar">
      {bands.map((x) => (
        <span key={x.b} style={{ flex: x.total }}>
          <i style={{ width: `${Math.round((100 * x.solved) / x.total)}%`, background: BAND_COLOR[x.b] }} />
        </span>
      ))}
    </div>
  );
}

function Badge({ row }: { row: Row }) {
  const style = (bg: string, fg: string): CSSProperties => ({ background: bg, color: fg });
  if (row.state === "cur") return <span className="tc-badge" style={style("var(--cab)", "var(--ca)")}>NOW ON</span>;
  if (row.state === "done") return <span className="tc-badge" style={style("var(--grn-bg)", "var(--grn)")}>DONE</span>;
  if (row.state === "planned")
    return (
      <span className="tc-badge" style={{ border: "1px dashed var(--line)", color: "var(--dim)" }}>
        PLANNED
      </span>
    );
  if (row.tier === "sde3") return <span className="tc-badge" style={style("var(--vio-bg)", "var(--vio)")}>SDE-3</span>;
  return null;
}

function Foot({ row }: { row: Row }) {
  const live = row.live;
  if (row.state === "planned" || !live) return <span>not written yet · {row.planned} planned</span>;
  if (row.state === "done")
    return (
      <>
        <span>all {live.solved} solved · re-solves keep it fresh</span>
        <span className="tc-go">review ›</span>
      </>
    );
  if (row.state === "ahead")
    return (
      <>
        <span>start fresh · {live.stages[0]?.name}</span>
        <span className="tc-go">start ›</span>
      </>
    );
  const stage = live.stages.find((s) => s.solved < s.ready);
  return (
    <>
      <span>resume · {stage?.name}</span>
      <span className="tc-go">resume ›</span>
    </>
  );
}

function TrackCard({ row }: { row: Row }) {
  const live = row.live;
  const total = live?.total ?? row.planned;
  const pct = live && live.total ? Math.round((100 * live.solved) / live.total) : 0;
  const stages = live?.stages ?? [];
  const body = (
    <>
      <div className="tc-top">
        <span className="tc-num">{pad2(row.n)}</span>
        <span className="tc-kind">
          TRACK / {TIER[row.tier]} · {row.code}
        </span>
        <Badge row={row} />
      </div>
      <h3>{live?.name ?? row.name}</h3>
      <p dangerouslySetInnerHTML={{ __html: marked.parseInline(live?.summary || BLURB[row.code] || "", { async: false }) }} />
      <div className="tc-meta">
        <b>{total}</b> problems · {hours(minutesTotal(row))} · easy → hard
      </div>
      <div className="tc-tags">
        {stages.slice(0, 3).map((s) => (
          <span className="cpill" key={s.slug}>
            {s.name}
          </span>
        ))}
        {stages.length > 3 && <span className="cpill">+{stages.length - 3}</span>}
      </div>
      <div className="tc-prog">
        <span>progress</span>
        <span>
          {row.state === "planned" ? (
            "—"
          ) : (
            <>
              <b>
                {live!.solved} / {live!.total}
              </b>{" "}
              · {pct}%
            </>
          )}
        </span>
      </div>
      <BandBar row={row} />
      <div className="tc-foot">
        <Foot row={row} />
      </div>
    </>
  );
  return live && row.state !== "planned" ? (
    <Link className={`tcard ${row.state}`} to="/t/$track" params={{ track: live.slug }}>
      {body}
    </Link>
  ) : (
    <div className="tcard planned" aria-disabled="true">
      {body}
    </div>
  );
}

function TrackRow({ row }: { row: Row }) {
  const live = row.live;
  const pct = live && live.total ? Math.round((100 * live.solved) / live.total) : 0;
  const inner = (
    <>
      <span className="n">{pad2(row.n)}</span>
      <span className="t">
        {live?.name ?? row.name}
        <small>
          {row.code} · {TIER[row.tier]}
          {row.state === "cur" ? " · now on" : ""}
        </small>
      </span>
      <span className="x hide" style={{ textAlign: "left" }}>
        {live?.total ?? row.planned} problems · {hours(minutesLeft(row))} left
      </span>
      <span className="hide">
        <BandBar row={row} />
      </span>
      <span className="x">{row.state === "planned" ? "planned" : `${pct}%`}</span>
    </>
  );
  return live && row.state !== "planned" ? (
    <Link className="trow" to="/t/$track" params={{ track: live.slug }}>
      {inner}
    </Link>
  ) : (
    <div className="trow" aria-disabled="true" style={{ opacity: 0.6 }}>
      {inner}
    </div>
  );
}

function Ring({ days }: { days: number }) {
  const r = 34;
  const c = 2 * Math.PI * r;
  const f = Math.min(1, days / 7);
  return (
    <div className="nu-ring">
      <svg viewBox="0 0 78 78" aria-hidden="true">
        <circle cx="39" cy="39" r={r} fill="none" stroke="var(--line2)" strokeWidth="5" />
        {days > 0 && (
          <circle cx="39" cy="39" r={r} fill="none" stroke="var(--ca)" strokeWidth="5" strokeLinecap="round" strokeDasharray={`${(c * f).toFixed(1)} ${c.toFixed(1)}`} />
        )}
      </svg>
      <div>
        <b>{days}</b>
        <span>{days === 1 ? "DAY" : "DAYS"}</span>
      </div>
    </div>
  );
}

const REASON: Record<NextUp["reason"], string> = {
  resume: "You started this one and haven't solved it yet.",
  current: "It's the next unsolved problem in the track you're working on.",
  start: "It's the first unsolved problem in the recommended order.",
};

function NextUpCard({ next, streak }: { next: NextUp; streak: number }) {
  const [mode, modeColor] = MODE_LABEL[next.mode];
  const after = Math.min(100, next.readiness + next.gain);
  return (
    <section className="nextup" aria-label="Next up">
      <Ring days={streak} />
      <div className="nu-k">
        <i />
        <span style={{ color: "var(--ca)" }}>NEXT UP</span>
        <span style={{ color: "var(--dim)" }}>
          {next.track_code} · {next.stage_name.toUpperCase()}
        </span>
      </div>
      <div className="nu-sub">
        {streak > 0 ? (
          <>
            <b>{streak}-day streak</b>, keep it going.
          </>
        ) : (
          <>
            <b>No streak yet.</b> Solve one today to start it.
          </>
        )}{" "}
        {REASON[next.reason]}
      </div>
      <div className="nu-main">
        <h2>{next.title}</h2>
        {next.excerpt && <p dangerouslySetInnerHTML={{ __html: marked.parseInline(next.excerpt, { async: false }) }} />}
        <div className="pills">
          <span className="cpill" style={{ color: BAND_COLOR[next.level] }}>
            {next.level}
          </span>
          <span className="cpill" style={{ color: modeColor }}>
            {mode}
          </span>
          <span className="cpill">{next.track_name}</span>
          <span className="cpill">~{MINUTES[next.level]}m</span>
        </div>
      </div>
      <div className="nu-gain">
        <span>
          {next.track_code} READINESS · {Math.round(next.readiness)}%
        </span>
        <span style={{ color: "var(--ca)" }}>+{next.gain}% IF UNASSISTED</span>
      </div>
      <div className="nu-bar">
        <span style={{ width: `${next.readiness}%`, background: "var(--ca)" }} />
        <span style={{ width: `${after - next.readiness}%`, background: "var(--ca)", opacity: 0.4 }} />
      </div>
      <Link className="nu-go" to="/p/$id" params={{ id: next.problem_id }}>
        Solve in the workspace →
      </Link>
    </section>
  );
}

const OUTCOME_COLOR = { solved: "var(--grn)", assisted: "var(--acc)", failing: "var(--bad)", started: "var(--dim)" } as const;

function Rail({ activity, sections, live, due }: { activity?: Activity; sections: readonly Section[]; live: TrackSummary[]; due: ReviewItem[] }) {
  const shade = (n: number) => (n === 0 ? "var(--line2)" : `color-mix(in oklch, var(--ca) ${Math.min(100, 25 + n * 15)}%, transparent)`);
  const readiness = sections.map((s) => {
    const ts = live.filter((t) => t.section === s && t.ready > 0);
    const w = (t: TrackSummary) => (t.tier === "core" ? 2 : 1);
    const total = ts.reduce((n, t) => n + w(t), 0);
    return { s, pct: total ? Math.round(ts.reduce((n, t) => n + t.readiness * w(t), 0) / total) : null };
  });
  return (
    <aside className="cat-rail" aria-label="Activity">
      <div className="rbox">
        <h4>
          <span>THIS WEEK</span>
          <span style={{ color: "var(--ca)" }}>{activity?.week_solved ?? 0} SOLVED</span>
        </h4>
        <div className="week">
          {(activity?.week ?? []).map((d) => (
            <div key={d.date}>
              <i style={{ background: shade(d.solved) }} title={`${d.date}: ${d.solved} solved`} />
              {new Date(`${d.date}T00:00`).toLocaleDateString(undefined, { weekday: "narrow" })}
            </div>
          ))}
        </div>
        <div className="rstat">
          <span>unassisted</span>
          <b>
            {activity?.week_unassisted ?? 0} of {activity?.week_solved ?? 0}
          </b>
        </div>
      </div>
      <div className="rbox">
        <h4>
          <span>RECENT</span>
        </h4>
        {activity?.recent.length ? (
          activity.recent.map((r) => (
            <Link key={r.problem_id + r.at} className="ritem" to="/p/$id" params={{ id: r.problem_id }}>
              <i style={{ background: OUTCOME_COLOR[r.outcome] }} />
              <span>{r.title}</span>
              <small>
                {r.track} · {r.detail}
              </small>
            </Link>
          ))
        ) : (
          <p className="rempty">Nothing yet. Your attempts show up here.</p>
        )}
      </div>
      {due.length > 0 && (
        <div className="rbox">
          <h4>
            <span>RE-SOLVE DUE</span>
            <Link to="/progress" hash="reviews" style={{ color: "var(--vio)" }}>
              {due.length} →
            </Link>
          </h4>
          {due.slice(0, 4).map((r) => (
            <Link key={r.problem_id} className="ritem" to="/progress" hash="reviews">
              <i style={{ background: "var(--vio)" }} />
              <span>{r.title}</span>
              <small>
                {r.track} · {r.days_overdue > 0 ? `${r.days_overdue}d late` : "today"}
              </small>
            </Link>
          ))}
        </div>
      )}
      <div className="rbox">
        <h4>
          <span>READINESS</span>
        </h4>
        {readiness.map(({ s, pct }) => (
          <div className="rmeter" key={s}>
            <span>{SECTION_NAMES[s]}</span>
            <em style={{ color: pct === null ? "var(--dim)" : pctColor(pct) }}>{pct === null ? "—" : `${pct}%`}</em>
            <i>
              <b style={{ width: `${pct ?? 0}%`, background: pct === null ? "transparent" : pctColor(pct) }} />
            </i>
          </div>
        ))}
      </div>
    </aside>
  );
}

/** The soft light that follows the pointer over a track card: its position is passed to the stylesheet. */
function pointerLight(e: React.PointerEvent<HTMLElement>) {
  const card = (e.target as HTMLElement).closest<HTMLElement>(".tcard");
  if (!card) return;
  const r = card.getBoundingClientRect();
  card.style.setProperty("--mx", `${e.clientX - r.left}px`);
  card.style.setProperty("--my", `${e.clientY - r.top}px`);
}

export function SectionPage({ area }: { area: NavArea }) {
  const copy = COPY[area];
  const sections: readonly Section[] = NAV_SECTIONS[area];
  const tracks = useQuery({ queryKey: ["tracks"], queryFn: api.tracks });
  const activity = useQuery({ queryKey: ["activity", area], queryFn: () => api.activity(sections) });
  const reviews = useQuery({ queryKey: ["reviews"], queryFn: api.reviews });
  const due = (reviews.data?.queue ?? []).filter((r) => r.days_overdue >= 0 && sections.includes(sectionOf(r.track)));
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState("all");
  const [view, setView] = useStored<"grid" | "list">("anneal-catalog-view", "grid");
  const search = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setQ("");
    setFilter("all");
  }, [area]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const typing = e.target instanceof HTMLElement && e.target.closest("input, textarea, [contenteditable]");
      if (e.key === "/" && !typing) {
        e.preventDefault();
        search.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const live = new Map((tracks.data ?? []).map((t) => [t.code, t]));
  // Only a track you've actually worked in is "now on"; a first pick is just a suggestion.
  const next = activity.data?.next;
  const current = next && next.reason !== "start" ? next.track_code : undefined;
  const order = (code: string) => (area === "dsa" ? DSA_ORDER.indexOf(code) : PLANNED.findIndex((t) => t.code === code));
  const rows: Row[] = PLANNED.filter((t) => sections.includes(sectionOf(t.code)))
    .sort((a, b) => order(a.code) - order(b.code))
    .map((t, i) => {
      const l = live.get(t.code);
      return { code: t.code, name: t.name, tier: t.tier, planned: t.planned, n: i + 1, live: l, state: stateOf(l, current) };
    });

  const needle = q.trim().toLowerCase();
  const test = FILTERS.find((f) => f[0] === filter)?.[2] ?? (() => true);
  const shown = (r: Row) =>
    test(r) &&
    (!needle ||
      [r.code, r.live?.name ?? r.name, r.live?.summary ?? BLURB[r.code] ?? "", ...(r.live?.stages.map((s) => s.name) ?? [])]
        .join(" ")
        .toLowerCase()
        .includes(needle));
  const problems = rows.reduce((n, r) => n + Math.max(r.planned, r.live?.total ?? 0), 0);
  const left = rows.reduce((n, r) => n + (r.state === "done" ? 0 : minutesLeft(r)), 0);

  const groups = (sections.length > 1 ? sections : [null]).map((s) => {
    const list = rows.filter((r) => (!s || sectionOf(r.code) === s) && shown(r));
    if (!list.length) return null;
    return (
      <div key={s ?? "all"} style={{ display: "contents" }}>
        <div className="flabel">{s ? `${SECTION_NAMES[s].toUpperCase()} · ${list.length}` : "ALL TRACKS · IN RECOMMENDED ORDER"}</div>
        {view === "grid" ? (
          <div className="tgrid" onPointerMove={pointerLight}>
            {list.map((r) => (
              <TrackCard key={r.code} row={r} />
            ))}
          </div>
        ) : (
          <div className="tlist">
            {list.map((r) => (
              <TrackRow key={r.code} row={r} />
            ))}
          </div>
        )}
      </div>
    );
  });

  return (
    <>
      <Header area={area} />
      <main className="page" style={{ "--ca": `var(--${copy.color})`, "--cab": `var(--${copy.color}-bg)` } as CSSProperties}>
        <div className="wrap">
          <section className="cat-top">
            <div style={{ minWidth: 0, flex: "1 1 520px" }}>
              <div className="eyebrow">
                <span style={{ color: "var(--ca)" }}>{copy.eyebrow}</span>
                <span>/</span>
                <span>TRACKS</span>
              </div>
              <h1 className="h1 md">
                {copy.title[0]}
                <span style={{ color: "var(--ca)" }}>{copy.title[1]}</span>
              </h1>
              <p className="lead">{copy.lead}</p>
            </div>
            <div className="cat-stats">
              <div>
                <b>
                  <CountUp value={rows.length} />
                </b>
                <span>TRACKS</span>
              </div>
              <div>
                <b>
                  <CountUp value={problems} />
                </b>
                <span>PROBLEMS</span>
              </div>
              <div>
                <b>
                  <CountUp value={left} format={hours} />
                </b>
                <span>TO FINISH</span>
              </div>
            </div>
          </section>
          {tracks.isError && <p className="notice bad">Couldn't reach the API. Is `cargo run -p anneal-api` running?</p>}
          <div className="cat-body">
            <div className="cat-main">
              {activity.data?.next && <NextUpCard next={activity.data.next} streak={activity.data.streak} />}
              <div className="cat-tools">
                <label className="cat-search">
                  <span aria-hidden="true" style={{ color: "var(--dim)" }}>
                    ⌕
                  </span>
                  <input
                    ref={search}
                    type="search"
                    placeholder="search tracks, stages, topics…"
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    aria-label="Search tracks"
                  />
                  <kbd>/</kbd>
                </label>
                <div className="seg slide" role="group" aria-label="View" style={{ "--i": view === "grid" ? 0 : 1 } as React.CSSProperties}>
                  {(["grid", "list"] as const).map((v) => (
                    <button key={v} className={view === v ? "on" : ""} aria-pressed={view === v} onClick={() => setView(v)}>
                      {v === "grid" ? "▦ grid" : "☰ list"}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flabel">FILTER BY</div>
              <div className="fchips">
                {FILTERS.map(([key, label, fn]) => {
                  const n = rows.filter(fn).length;
                  if (!n && key !== "all") return null;
                  return (
                    <button key={key} className={`fchip${filter === key ? " on" : ""}`} aria-pressed={filter === key} onClick={() => setFilter(key)}>
                      {label}
                      <small>{n}</small>
                    </button>
                  );
                })}
              </div>
              {groups.some(Boolean) ? (
                groups
              ) : (
                <div className="cat-empty">
                  No tracks match.{" "}
                  <button
                    style={{ color: "var(--ca)" }}
                    onClick={() => {
                      setQ("");
                      setFilter("all");
                    }}
                  >
                    Clear filters
                  </button>
                </div>
              )}
            </div>
            <Rail activity={activity.data} sections={sections} live={tracks.data ?? []} due={due} />
          </div>
        </div>
      </main>
    </>
  );
}
