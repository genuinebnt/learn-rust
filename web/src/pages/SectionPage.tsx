import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api, type Section, type TrackSummary } from "../api";
import { Header } from "../components/Header";
import { Sech, pctColor } from "../components/bits";
import { NAV_SECTIONS, PLANNED, SECTION_NAMES, type NavArea, sectionOf } from "../curriculum";

const COPY: Record<NavArea, { eyebrow: string; accent: string; title: [string, string]; lead: string }> = {
  dsa: {
    eyebrow: "DSA",
    accent: "var(--acc)",
    title: ["Fourteen tracks, ", "easy to hard."],
    lead: "Every track climbs from easy to medium to hard, and every problem is solved the way Rust wants it: index-based graphs, Option<Box<Node>> lists, heaps with Reverse<T>.",
  },
  rust: {
    eyebrow: "RUST",
    accent: "var(--vio)",
    title: ["The Rust interviewers ", "actually probe."],
    lead: "Language, standard library, concurrency and systems. Each track climbs from using the API, to understanding why it behaves that way, to building a simplified version yourself.",
  },
  build: {
    eyebrow: "BUILD",
    accent: "var(--grn)",
    title: ["Services and systems, ", "built from tests."],
    lead: "Backend tracks drill axum, tower, sqlx and resilience patterns. Machine coding gives you 60 to 90 minutes and a test suite.",
  },
};

const TIER = { core: "CORE", light: "LIGHT", sde3: "SDE-3" } as const;

function Tile({ code, name, tier, planned, live }: { code: string; name: string; tier: keyof typeof TIER; planned: number; live?: TrackSummary }) {
  const pct = live && live.total ? Math.round((100 * live.solved) / live.total) : 0;
  const color = live ? pctColor(pct) : "var(--dim)";
  const body = (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 6 }}>
        <span className="m" style={{ fontSize: 10.5, letterSpacing: ".14em", color: "var(--dim)" }}>
          {code}
        </span>
        <span className="m" style={{ fontSize: 9.5, letterSpacing: ".14em", color: tier === "core" ? "var(--mut)" : "var(--dim)" }}>
          {TIER[tier]}
        </span>
      </div>
      <span className="n">{name}</span>
      <span className="p" style={{ color }}>
        {live ? `${pct}%` : "—"}
      </span>
      <div>
        <div className="bar">
          {Array.from({ length: 10 }, (_, i) => (
            <span key={i} style={{ background: live && i < Math.round(pct / 10) ? color : "var(--line2)" }} />
          ))}
        </div>
        <div className="meta">{live ? `${live.solved} / ${live.total} solved · ${live.ready} ready` : `not written yet · ${planned} planned`}</div>
      </div>
    </>
  );
  return live ? (
    <Link className="tile" to="/t/$track" params={{ track: live.slug }}>
      {body}
    </Link>
  ) : (
    <div className="tile tile-planned" aria-disabled="true">
      {body}
    </div>
  );
}

export function SectionPage({ area }: { area: NavArea }) {
  const tracks = useQuery({ queryKey: ["tracks"], queryFn: api.tracks });
  const live = new Map((tracks.data ?? []).map((t) => [t.code, t]));
  const copy = COPY[area];
  const sections: readonly Section[] = NAV_SECTIONS[area];
  const inArea = PLANNED.filter((t) => sections.includes(sectionOf(t.code)));
  const written = inArea.filter((t) => live.has(t.code));
  return (
    <>
      <Header area={area} />
      <main className="page">
        <div className="wrap">
          <section className="hero solo">
            <div>
              <div className="eyebrow">
                <span style={{ color: copy.accent }}>{copy.eyebrow}</span>
                <span>/</span>
                <span>{inArea.length} TRACKS</span>
                <span>/</span>
                <span>{written.length} WRITTEN</span>
              </div>
              <h1 className="h1 md">
                {copy.title[0]}
                <span style={{ color: copy.accent }}>{copy.title[1]}</span>
              </h1>
              <p className="lead">{copy.lead}</p>
            </div>
          </section>
          {tracks.isError && <p className="notice bad">Couldn't reach the API. Is `cargo run -p anneal-api` running?</p>}
          {sections.map((s) => {
            const list = inArea.filter((t) => sectionOf(t.code) === s);
            const solved = list.reduce((n, t) => n + (live.get(t.code)?.solved ?? 0), 0);
            return (
              <section className="sec" key={s} style={{ paddingTop: 48 }}>
                <Sech title={`${SECTION_NAMES[s].toUpperCase()} · ${list.length} TRACKS`} caption={`${solved} solved`} />
                <div className="ttiles">
                  {list.map((t) => (
                    <Tile key={t.code} {...t} live={live.get(t.code)} />
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </main>
    </>
  );
}
