import { Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { api, type Grade, type MockConfig, type MockData, type MockRound } from "../api";
import { Header } from "../components/Header";
import { DIFF, leetcode, niceDate } from "../dsa";
import {
  BANDS,
  FAVOUR,
  MOCK_LISTS,
  MOCK_STATUS,
  PRESETS,
  clock,
  countBy,
  currentIndex,
  defaultConfig,
  draw,
  elapsed,
  isLogged,
  limitOf,
  mmss,
  newRound,
  onProblem,
  paceMinutes,
  poolOf,
  shortfall,
  slotsOf,
  suggested,
  summary,
  warning,
  type Round,
} from "../mock";

const ROUND_KEY = "anneal-mock-round";

function loadRound(): Round | null {
  try {
    const raw = localStorage.getItem(ROUND_KEY);
    return raw ? (JSON.parse(raw) as Round) : null;
  } catch {
    return null;
  }
}

function storeRound(r: Round | null) {
  try {
    if (r) localStorage.setItem(ROUND_KEY, JSON.stringify(r));
    else localStorage.removeItem(ROUND_KEY);
  } catch {
    // Private windows can refuse storage; the round still runs for this visit.
  }
}

/** A timed round of random LeetCode problems, set up the way you choose (docs/DSA.md, decision 25). */
export function MockPage() {
  const q = useQuery({ queryKey: ["dsa-mock"], queryFn: api.mock });
  return (
    <>
      <Header area="dsa" />
      <main className="page" style={{ "--ca": "var(--acc)", "--cab": "var(--acc-bg)" } as CSSProperties}>
        {q.data ? (
          <MockApp data={q.data} />
        ) : (
          <div className="wrap" style={{ paddingBlock: 28 }}>
            <p className="rempty">{q.isError ? "Couldn't reach the API." : "Loading…"}</p>
          </div>
        )}
      </main>
    </>
  );
}

function MockApp({ data }: { data: MockData }) {
  const qc = useQueryClient();
  const [round, setRound] = useState<Round | null>(loadRound);
  const [config, setConfig] = useState<MockConfig>(() => ({ ...defaultConfig(), ...data.saved?.last }));
  const [drawError, setDrawError] = useState<string | null>(null);
  const finishing = useRef(false);
  const remember = useMutation({ mutationFn: api.saveMock });

  const update = useCallback((fn: (r: Round) => Round) => {
    setRound((cur) => {
      if (!cur) return cur;
      const next = fn(cur);
      storeRound(next);
      return next;
    });
  }, []);

  const begin = (c: MockConfig) => {
    const pool = poolOf(data.problems, c, data.today);
    const picked = draw(pool, c, data.today);
    if (!picked) {
      setDrawError(shortfall(pool, c) ?? "Couldn't draw problems for this setup.");
      return false;
    }
    setDrawError(null);
    setConfig(c);
    finishing.current = false;
    const r = newRound(c, picked.map((p) => p.id), Date.now());
    storeRound(r);
    setRound(r);
    remember.mutate({ ...data.saved, last: c });
    return true;
  };

  const finish = (r: Round) => {
    if (r.ended != null || finishing.current) return;
    finishing.current = true;
    const now = Date.now();
    const ended = { ...r, ended: elapsed(r, now), pausedAt: null };
    const body = summary(ended, now);
    storeRound({ ...ended, saved: true });
    setRound({ ...ended, saved: true });
    api
      .finishMock({ config: r.config, ...body })
      .catch(() => undefined)
      .finally(() => {
        void qc.invalidateQueries({ queryKey: ["dsa-mock"] });
        void qc.invalidateQueries({ queryKey: ["dsa"] });
        void qc.invalidateQueries({ queryKey: ["tracks"] });
      });
  };

  const leave = (keepConfig: boolean) => {
    if (keepConfig && round) setConfig(round.config);
    storeRound(null);
    setRound(null);
    finishing.current = false;
  };

  if (round && round.ended == null) return <Live data={data} round={round} update={update} onFinish={finish} />;
  if (round) {
    return (
      <Result
        data={data}
        round={round}
        onAgain={() => {
          if (!begin(round.config)) leave(true);
        }}
        onChange={() => leave(true)}
      />
    );
  }
  return <Setup data={data} initial={config} onStart={begin} error={drawError} />;
}

// ---------------------------------------------------------------- setup

function Step({ value, onChange, min, max, step = 1, label, wide, unit }: { value: number; onChange: (n: number) => void; min: number; max: number; step?: number; label: string; wide?: boolean; unit?: string }) {
  return (
    <span className={`m-stepper${wide ? " wide" : ""}`} role="group" aria-label={label}>
      <button aria-label={`less ${label}`} disabled={value <= min} onClick={() => onChange(Math.max(min, value - step))}>
        <svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 6h8" /></svg>
      </button>
      <b aria-live="polite">
        {value}
        {unit && <small>{unit}</small>}
      </b>
      <button aria-label={`more ${label}`} disabled={value >= max} onClick={() => onChange(Math.min(max, value + step))}>
        <svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 6h8M6 2v8" /></svg>
      </button>
    </span>
  );
}

function Toggle({ on, onClick, title, hint, disabled }: { on: boolean; onClick: () => void; title: string; hint?: string; disabled?: boolean }) {
  return (
    <button className={`m-tog${on ? " on" : ""}`} onClick={onClick} disabled={disabled} role="switch" aria-checked={on}>
      <span className="sw" />
      <span>
        <b>{title}</b>
        {hint && <span className="s">{hint}</span>}
      </span>
    </button>
  );
}

const toggle = (list: string[], v: string) => (list.includes(v) ? list.filter((x) => x !== v) : [...list, v]);

function Setup({ data, initial, onStart, error }: { data: MockData; initial: MockConfig; onStart: (c: MockConfig) => void; error: string | null }) {
  const qc = useQueryClient();
  const [c, setC] = useState<MockConfig>(initial);
  const [preset, setPreset] = useState("custom");
  const [coQuery, setCoQuery] = useState("");
  const [allCo, setAllCo] = useState(false);
  const [naming, setNaming] = useState(false);
  const [name, setName] = useState("");
  const presets = data.saved?.presets ?? [];
  const savePresets = useMutation({
    mutationFn: (next: typeof presets) => api.saveMock({ ...data.saved, presets: next }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["dsa-mock"] }),
  });

  const edit = (fn: (c: MockConfig) => MockConfig) => {
    setC(fn);
    setPreset("custom");
  };

  const pool = useMemo(() => poolOf(data.problems, c, data.today), [data, c]);
  const have = countBy(pool);
  const problem = shortfall(pool, c);
  const need = slotsOf(c);

  // Counts shown beside each choice: what the other settings leave.
  const byTopic = useMemo(() => {
    const m = new Map<string, number>();
    for (const p of poolOf(data.problems, { ...c, topics: {} }, data.today)) m.set(p.pattern, (m.get(p.pattern) ?? 0) + 1);
    return m;
  }, [data, c]);
  const byCompany = useMemo(() => {
    const m = new Map<string, number>();
    const g = new Map<string, number>();
    for (const p of poolOf(data.problems, { ...c, groups: [], companies: [], recent: false }, data.today)) {
      const seenGroups = new Set<string>();
      for (const co of p.companies) {
        m.set(co.name, (m.get(co.name) ?? 0) + 1);
        seenGroups.add(co.group);
      }
      for (const name of seenGroups) g.set(name, (g.get(name) ?? 0) + 1);
    }
    return { companies: m, groups: g };
  }, [data, c]);
  const listCount = (key: string) => data.problems.filter((p) => !p.premium && p.lists.includes(key as never)).length;

  const allCompanies = useMemo(
    () =>
      [...new Set(data.company_groups.flatMap((g) => g.companies))]
        .map((n) => ({ name: n, n: byCompany.companies.get(n) ?? 0 }))
        .filter((x) => x.n > 0 || c.companies.includes(x.name))
        .sort((a, b) => b.n - a.n || a.name.localeCompare(b.name)),
    [data.company_groups, byCompany, c.companies],
  );
  const q = coQuery.trim().toLowerCase();
  const matching = q ? allCompanies.filter((x) => x.name.toLowerCase().includes(q)) : allCompanies;
  const shownCo = q || allCo ? matching : matching.slice(0, 8);

  const topicCounts = Object.values(c.topics);
  const included = topicCounts.filter((v) => v === 1).length;
  const excluded = topicCounts.filter((v) => v === -1).length;
  const cycleTopic = (code: string) =>
    edit((cur) => {
      const topics = { ...cur.topics };
      const v = topics[code];
      if (v === undefined) topics[code] = 1;
      else if (v === 1) topics[code] = -1;
      else delete topics[code];
      return { ...cur, topics };
    });

  const slots = c.anyDiff ? Array.from({ length: c.anyCount }, () => 1) : c.mix.flatMap((k, i) => Array.from({ length: k }, () => i));
  const perTotal = paceMinutes(c);
  const warnings: { cls: string; text: string }[] = [];
  if (problem) warnings.push({ cls: "m-bad", text: problem });
  if (!problem && error) warnings.push({ cls: "m-bad", text: error });
  if (c.format === "total" && perTotal > c.total * 1.25) warnings.push({ cls: "m-warn", text: `The suggested times add up to ${perTotal} min and the round is only ${c.total} min. Lengthen the round or ask for fewer problems.` });
  if (c.favour === "weak" && !pool.some((p) => p.state.last_grade === "again" || p.state.last_grade === "hard" || (p.state.due && p.state.due <= data.today))) {
    warnings.push({ cls: "m-warn", text: "Nothing here is marked weak yet, so this will draw uniformly." });
  }
  const timerName = c.format === "total" ? `Countdown, ${c.total}:00` : c.format === "per" ? "Countdown per problem" : "Stopwatch";

  return (
    <div className="wrap m-setup" style={{ paddingBlock: 28 }}>
      <div className="eyebrow">
        <Link to="/dsa" style={{ color: "var(--ca)" }}>DSA</Link>
        <span>/</span>
        <span>MOCK INTERVIEW</span>
        <span>/</span>
        <span>{data.rounds.length} ROUND{data.rounds.length === 1 ? "" : "S"} TAKEN</span>
      </div>
      <h1 className="h1 md">Timed, drawn at random</h1>
      <p className="lead">Choose what can be drawn and how the clock runs. The problems are drawn when you start, you solve them on LeetCode, and you log each one as you finish.</p>

      <div className="p-grid">
        <div className="p-col">
          <section className="p-card">
            <h2>START FROM <em>fills the problem count and time; change anything after</em></h2>
            <div className="m-presets" role="group" aria-label="Presets">
              {PRESETS.map((p) => (
                <button key={p.key} className={`m-preset${preset === p.key ? " on" : ""}`} aria-pressed={preset === p.key} onClick={() => { setC(p.apply(c)); setPreset(p.key); }}>
                  <b>{p.name}</b>
                  <span>{p.detail}</span>
                </button>
              ))}
              {presets.map((p) => (
                <span key={p.name} className={`m-preset${preset === `saved:${p.name}` ? " on" : ""}`}>
                  <button className="body" aria-pressed={preset === `saved:${p.name}`} onClick={() => { setC(p.config); setPreset(`saved:${p.name}`); }}>
                    <b>{p.name}</b>
                    <span>{describe(p.config, data)}</span>
                  </button>
                  <button className="x" aria-label={`Delete preset ${p.name}`} onClick={() => savePresets.mutate(presets.filter((x) => x.name !== p.name))}>×</button>
                </span>
              ))}
            </div>
          </section>

          <div className="m-pair"><section className="p-card">
            <h2>WHERE PROBLEMS COME FROM <em>{c.lists.length} selected</em></h2>
            <div className="m-chips">
              {MOCK_LISTS.map(([key, label]) => (
                <button key={key} className={`m-chip${c.lists.includes(key) ? " on" : ""}`} aria-pressed={c.lists.includes(key)} onClick={() => edit((cur) => ({ ...cur, lists: cur.lists.includes(key) ? (cur.lists.length > 1 ? toggle(cur.lists, key) : cur.lists) : [...cur.lists, key] }))}>
                  {label}<span className="n">{listCount(key)}</span>
                </button>
              ))}
            </div>
            <p className="p-hint">Practice problems are the other LeetCode problems for each technique. They never schedule reviews. Premium problems are always left out.</p>
          </section><section className="p-card">
            <h2>YOUR HISTORY <em>which of those problems can be drawn</em></h2>
            <div className="m-opts" role="group" aria-label="History">
              {MOCK_STATUS.map(([key, label]) => (
                <button key={key} className={c.status === key ? "on" : ""} onClick={() => edit((cur) => ({ ...cur, status: key }))}>{label}</button>
              ))}
            </div>
            <p className="p-hint">{MOCK_STATUS.find(([k]) => k === c.status)?.[2]}</p>
          </section></div>
          <section className="p-card">
            <h2>TOPICS <em>{included || excluded ? `${included} included · ${excluded} excluded` : "click once to include, twice to exclude, three times to clear"}</em></h2>
            <div className="m-chips">
              {data.patterns.map((pt) => {
                const v = c.topics[pt.code];
                return (
                  <button key={pt.code} className={`m-chip${v === 1 ? " inc" : v === -1 ? " exc" : ""}`} onClick={() => cycleTopic(pt.code)} aria-label={`${pt.name}: ${v === 1 ? "included" : v === -1 ? "excluded" : "allowed"}`}>
                    <span className="mk">{v === 1 ? "✓" : v === -1 ? "✕" : ""}</span>
                    {pt.name}
                    <span className="n">{byTopic.get(pt.code) ?? 0}</span>
                  </button>
                );
              })}
            </div>
            <p className="p-hint">With no topic included, every topic is allowed except the ones you exclude.</p>
          </section>
          <section className="p-card">
            <h2>COMPANIES <em>{c.groups.length + c.companies.length ? [...c.groups, ...c.companies].slice(0, 3).join(", ") + (c.groups.length + c.companies.length > 3 ? ` +${c.groups.length + c.companies.length - 3}` : "") + (c.recent ? " · recent" : "") : c.recent ? "any company · recent" : "any company"}</em></h2>
            <div className="m-chips">
              {data.company_groups.map((g) => (
                <button key={g.name} className={`m-chip${c.groups.includes(g.name) ? " on" : ""}`} aria-pressed={c.groups.includes(g.name)} onClick={() => edit((cur) => ({ ...cur, groups: toggle(cur.groups, g.name) }))}>
                  {g.name}<span className="n">{byCompany.groups.get(g.name) ?? 0}</span>
                </button>
              ))}
            </div>
            <div className="m-chips">
              {shownCo.map((x) => (
                <button key={x.name} className={`m-chip${c.companies.includes(x.name) ? " on" : ""}`} aria-pressed={c.companies.includes(x.name)} onClick={() => edit((cur) => ({ ...cur, companies: toggle(cur.companies, x.name) }))}>
                  {x.name}<span className="n">{x.n}</span>
                </button>
              ))}
              {!q && matching.length > 8 && (
                <button className="m-more" onClick={() => setAllCo(!allCo)}>{allCo ? "show fewer" : `+${matching.length - 8} more`}</button>
              )}
            </div>
            <div className="p-row" style={{ alignItems: "center" }}>
              <input className="m-search" value={coQuery} onChange={(e) => setCoQuery(e.target.value)} placeholder="Find a company" aria-label="Find a company" />
              <Toggle on={c.recent} onClick={() => edit((cur) => ({ ...cur, recent: !cur.recent }))} title="Asked in the last 6 months" />
            </div>
            <p className="p-hint">A problem can be drawn if any selected company asks it.</p>
          </section>
          <section className="p-card">
            <h2>DIFFICULTY <em>{c.anyDiff ? "any difficulty" : "how many of each"}</em></h2>
            {c.anyDiff ? (
              <div className="p-row">
                <div className="p-fld">
                  <span>NUMBER OF PROBLEMS</span>
                  <Step label="problems" value={c.anyCount} min={1} max={6} onChange={(anyCount) => edit((cur) => ({ ...cur, anyCount }))} />
                </div>
              </div>
            ) : (
              <div className="m-mix">
                {BANDS.map((band, i) => {
                  const k = c.mix[i] ?? 0;
                  return (
                    <div key={band} className={`m-mixc${k > have[i]! ? " short" : ""}`}>
                      <div className="t">
                        <span className={`m-${band[0]}`}>{band.toUpperCase()}</span>
                        <span>{have[i]} can be drawn</span>
                      </div>
                      <Step wide label={band} value={k} min={0} max={4} onChange={(n) => edit((cur) => ({ ...cur, mix: cur.mix.map((x, j) => (j === i ? n : x)) as MockConfig["mix"] }))} />
                    </div>
                  );
                })}
              </div>
            )}
            <Toggle on={c.anyDiff} onClick={() => edit((cur) => ({ ...cur, anyDiff: !cur.anyDiff }))} title="Any difficulty" hint="Draw the number of problems without caring about easy, medium or hard." />
          </section><section className="p-card">
            <h2>HOW TO DRAW</h2>
            <div className="m-opts" role="group" aria-label="How to draw">
              {FAVOUR.map(([key, label]) => (
                <button key={key} className={c.favour === key ? "on" : ""} onClick={() => edit((cur) => ({ ...cur, favour: key }))}>{label}</button>
              ))}
            </div>
            <p className="p-hint">{FAVOUR.find(([k]) => k === c.favour)?.[2]}</p>
          </section>
          <section className="p-card">
            <h2>TIMERS</h2>
            <div className="p-fld">
              <span>FORMAT</span>
              <div className="m-opts" role="group" aria-label="Timer format">
                <button className={c.format === "total" ? "on" : ""} onClick={() => edit((cur) => ({ ...cur, format: "total" }))}>Countdown for the round</button>
                <button className={c.format === "per" ? "on" : ""} onClick={() => edit((cur) => ({ ...cur, format: "per" }))}>Countdown per problem</button>
                <button className={c.format === "up" ? "on" : ""} onClick={() => edit((cur) => ({ ...cur, format: "up" }))}>Stopwatch only</button>
              </div>
            </div>
            {c.format === "up" ? (
              <p className="p-hint">No limit. The clock counts up, and each problem shows its time against the suggested time ({c.per.join(" / ")} min for easy, medium, hard).</p>
            ) : (
              <div className="p-row">
                {c.format === "total" && (
                  <div className="p-fld">
                    <span>ROUND LENGTH, MINUTES</span>
                    <Step label="minutes" unit="min" value={c.total} min={10} max={180} step={5} onChange={(total) => edit((cur) => ({ ...cur, total }))} />
                  </div>
                )}
                {BANDS.map((band, i) => (
                  <div key={band} className="p-fld">
                    <span>{c.format === "total" ? "SUGGESTED, " : ""}{band.toUpperCase()} MIN</span>
                    <Step label={`${band} minutes`} unit="min" value={c.per[i] ?? 0} min={3} max={90} onChange={(n) => edit((cur) => ({ ...cur, per: cur.per.map((x, j) => (j === i ? n : x)) as MockConfig["per"] }))} />
                  </div>
                ))}
              </div>
            )}
            <div className="m-togs">
              <Toggle on={c.strict} onClick={() => edit((cur) => ({ ...cur, strict: !cur.strict }))} title="Strict: no pause" hint="The clock keeps running, like a real call. Turn off to allow Pause." />
              <Toggle on={c.blind} onClick={() => edit((cur) => ({ ...cur, blind: !cur.blind }))} title="Blind mode" hint="Hide topic, tags and companies until you log the problem." />
              <Toggle
                on={c.auto}
                disabled={c.format === "up"}
                onClick={() => edit((cur) => ({ ...cur, auto: !cur.auto }))}
                title={c.format === "per" ? "Move on at 0:00" : "End the round at 0:00"}
                hint={c.format === "per" ? "Off: the problem's clock turns red and counts overtime." : "Off: the clock turns red and counts overtime, and you decide when to stop."}
              />
              <Toggle on={c.warns} disabled={c.format === "up"} onClick={() => edit((cur) => ({ ...cur, warns: !cur.warns }))} title="Time warnings" hint="A banner at 10, 5 and 1 minute left." />
            </div>
          </section>

          {data.rounds.length > 0 && (
            <section className="p-card">
              <h2>PAST ROUNDS</h2>
              <div className="m-tw">
                <div className="m-tbl" style={{ minWidth: 560 }}>
                  <div className="m-tr m-hist th"><span>DATE</span><span>ROUND</span><span>RESULT</span><span>TIME</span></div>
                  {data.rounds.map((r) => (
                    <div key={r.id} className="m-tr m-hist">
                      <span>{new Date(r.finished_at).toLocaleDateString(undefined, { day: "numeric", month: "short" })}</span>
                      <span>{describe(r.config, data)}</span>
                      <span>{resultGlyphs(r)}</span>
                      <span>{mmss(r.seconds)}{r.config.format === "total" ? ` / ${mmss(r.config.total * 60)}` : ""}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}
        </div>

        <aside className="p-col">
          <section className="p-card p-res">
            <h2>YOUR ROUND</h2>
            <div className="p-big">{pool.length}<small>can be drawn</small></div>
            <div className="m-dist">
              {BANDS.map((band, i) => <span key={band} className={`m-pill m-${band[0]}`}>{DIFF[band][0]} {have[i]}</span>)}
            </div>
            <hr className="m-rule" />
            <div className="m-stack">
              {slots.length === 0 && <p className="p-hint">Pick at least one problem.</p>}
              {slots.map((band, j) => (
                <div key={j} className="m-slot">
                  <span className="no">{j + 1}</span>
                  <span className="ti">{c.anyDiff ? "Any difficulty" : <b className={`m-${BANDS[band]![0]}`} style={{ fontWeight: 600 }}>{DIFF[BANDS[band]!][0]}</b>} · hidden until you start</span>
                  <span className="tm">~{c.per[c.anyDiff ? 1 : band]}m</span>
                </div>
              ))}
            </div>
            {warnings.length > 0 && <div className="m-stack">{warnings.map((w) => <div key={w.text} className={w.cls}>{w.text}</div>)}</div>}
            <hr className="m-rule" />
            <dl className="p-kv">
              <div><dt>Problems</dt><dd>{need}</dd></div>
              <div><dt>Timer</dt><dd>{timerName}</dd></div>
              <div><dt>Time at suggested pace</dt><dd>{perTotal} min</dd></div>
              <div><dt>Pause</dt><dd>{c.strict ? "not allowed" : "allowed"}</dd></div>
              <div><dt>Topic and tags</dt><dd>{c.blind ? "hidden" : "shown"}</dd></div>
            </dl>
            <button className="m-go" disabled={!!problem} onClick={() => onStart(c)}>Draw and start the clock →</button>
            <p className="m-note">The problems are drawn when you press start, so you never see them early.</p>
          </section>
          <section className="p-card">
            <h2>SAVE THESE SETTINGS</h2>
            {naming ? (
              <form
                className="p-row"
                style={{ alignItems: "center" }}
                onSubmit={(e) => {
                  e.preventDefault();
                  const n = name.trim();
                  if (!n) return;
                  savePresets.mutate([...presets.filter((p) => p.name !== n), { name: n, config: c }]);
                  setPreset(`saved:${n}`);
                  setNaming(false);
                  setName("");
                }}
              >
                <input className="m-search" value={name} onChange={(e) => setName(e.target.value)} placeholder="Name this preset" aria-label="Preset name" maxLength={40} autoFocus />
                <button className="m-ghost" type="submit" disabled={!name.trim()}>Save</button>
                <button className="m-ghost" type="button" onClick={() => setNaming(false)}>Cancel</button>
              </form>
            ) : (
              <button className="m-ghost" onClick={() => setNaming(true)}>Save as a preset</button>
            )}
            
            <p className="m-note">The settings of your last round are remembered the next time you open this page.</p>
          </section>
        </aside>
      </div>
      <div className="m-dock">
        <span><b>{pool.length}</b> can be drawn · {need} problem{need === 1 ? "" : "s"}</span>
        <button className="m-go" disabled={!!problem} onClick={() => onStart(c)}>Start →</button>
      </div>
    </div>
  );
}

/** One line for a round's settings: "2 medium · Trees, Graphs · NeetCode 150". */
function describe(c: MockConfig, data: MockData): string {
  const parts: string[] = [];
  parts.push(c.anyDiff ? `${c.anyCount} problem${c.anyCount === 1 ? "" : "s"}` : BANDS.flatMap((b, i) => ((c.mix[i] ?? 0) > 0 ? [`${c.mix[i]} ${b}`] : [])).join(", ") || "no problems");
  const topics = Object.entries(c.topics).filter(([, v]) => v === 1).map(([code]) => data.patterns.find((p) => p.code === code)?.name ?? code);
  parts.push(topics.length ? topics.join(", ") : "any topic");
  parts.push(c.lists.map((l) => MOCK_LISTS.find(([k]) => k === l)?.[1] ?? l).join(" + "));
  if (c.groups.length + c.companies.length) parts.push([...c.groups, ...c.companies].join(", "));
  return parts.join(" · ");
}

const glyphOf = (g: Grade | null) => (g === "good" || g === "easy" ? "✓" : g === "hard" ? "½" : g === "again" ? "✗" : "–");
const resultGlyphs = (r: MockRound) => r.items.map((i) => glyphOf(i.grade)).join(" ");

// ---------------------------------------------------------------- live

function useNow(running: boolean): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    setNow(Date.now());
    if (!running) return;
    const t = window.setInterval(() => setNow(Date.now()), 250);
    return () => window.clearInterval(t);
  }, [running]);
  return now;
}

const WARN_TEXT: Record<number, string> = { 600: "10 minutes left.", 300: "5 minutes left.", 60: "1 minute left." };

function Live({ data, round, update, onFinish }: { data: MockData; round: Round; update: (fn: (r: Round) => Round) => void; onFinish: (r: Round) => void }) {
  const now = useNow(round.pausedAt == null);
  const byId = useMemo(() => new Map(data.problems.map((p) => [p.id, p])), [data.problems]);
  const c = round.config;
  const index = currentIndex(round);
  const problem = byId.get(round.ids[index] ?? "");
  const logged = isLogged(round);
  const band = problem?.difficulty ?? null;
  const time = clock(round, band, now);
  const limit = limitOf(c, band);
  const [banner, setBanner] = useState<string | null>(null);
  const [confirmEnd, setConfirmEnd] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const last = useRef(time.value);
  const lastKey = useRef(`${index}`);

  const advance = useCallback(
    (fn: (r: Round) => Round) => {
      update(fn);
    },
    [update],
  );

  // Warnings as the clock crosses 10, 5 and 1 minute, and the moves at 0:00.
  useEffect(() => {
    const key = `${index}`;
    if (lastKey.current !== key) {
      lastKey.current = key;
      last.current = time.value;
      setBanner(null);
      return;
    }
    if (c.format !== "up" && c.warns) {
      const w = warning(last.current, time.value, limit);
      if (w != null) {
        setBanner(WARN_TEXT[w] ?? null);
        const t = window.setTimeout(() => setBanner(null), 9000);
        last.current = time.value;
        return () => window.clearTimeout(t);
      }
    }
    last.current = time.value;
  }, [time.value, index, c.format, c.warns, limit]);

  useEffect(() => {
    if (!c.auto || c.format === "up" || time.value > 0 || round.pausedAt != null) return;
    if (c.format === "total") {
      onFinish(round);
    } else if (!logged) {
      const to = elapsed(round, Date.now());
      if (index + 1 < round.ids.length) advance((r) => ({ ...r, marks: [...r.marks, { grade: null, to, due: null }], starts: [...r.starts, to] }));
      else onFinish({ ...round, marks: [...round.marks, { grade: null, to, due: null }] });
    }
  }, [time.value, c.auto, c.format, round, logged, index, advance, onFinish]);

  useEffect(() => {
    const before = document.title;
    document.title = `${mmss(time.value)} · Mock round`;
    return () => {
      document.title = before;
    };
  }, [time.value]);

  if (!problem) {
    return (
      <div className="wrap" style={{ paddingBlock: 28 }}>
        <p className="rempty">A problem in this round is no longer in the catalog.</p>
        <button className="m-ghost" onClick={() => onFinish(round)}>End the round</button>
      </div>
    );
  }

  const log = async (grade: Grade) => {
    if (logged || busy) return;
    setBusy(true);
    setError(null);
    const to = elapsed(round, Date.now());
    try {
      const out = await api.logDsa(problem.id, grade);
      advance((r) => ({ ...r, marks: [...r.marks, { grade, to, due: out.due }] }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const skip = () => {
    const to = elapsed(round, Date.now());
    if (index + 1 < round.ids.length) advance((r) => ({ ...r, marks: [...r.marks, { grade: null, to, due: null }], starts: [...r.starts, to] }));
    else onFinish({ ...round, marks: [...round.marks, { grade: null, to, due: null }] });
  };
  const next = () => {
    const to = elapsed(round, Date.now());
    if (index + 1 < round.ids.length) advance((r) => ({ ...r, starts: [...r.starts, to] }));
    else onFinish(round);
  };
  const togglePause = () =>
    update((r) => {
      const t = Date.now();
      return r.pausedAt == null ? { ...r, pausedAt: t } : { ...r, pausedMs: r.pausedMs + (t - r.pausedAt), pausedAt: null };
    });

  const total = elapsed(round, now);
  const sug = suggested(c, problem.difficulty);
  const spent = onProblem(round, now);
  const mark = round.marks[index];
  const pct = c.format === "total" ? Math.min(100, (total / (c.total * 60)) * 100) : Math.min(100, (spent / Math.max(1, sug)) * 100);
  const overall = time.value < 0 && time.counting === "down";
  const showMeta = logged || !c.blind;
  const patternName = data.patterns.find((p) => p.code === problem.pattern)?.name ?? "";
  const lastOne = index + 1 >= round.ids.length;
  const clockLabel = c.format === "per" ? `PROBLEM ${index + 1} · ${time.value < 0 ? "OVERTIME" : "LEFT"}` : c.format === "up" ? "ELAPSED" : overall ? "OVERTIME" : "MOCK ROUND · LIVE";

  return (
    <>
      <div className="m-bar">
        <div className="m-clock">
          <span className="l">{clockLabel}</span>
          <span className={`c${time.counting === "down" && time.value < 0 ? " over" : time.counting === "down" && time.value <= 300 && limit > 300 ? " low" : ""}`} aria-live="off">
            {mmss(time.value)}
          </span>
        </div>
        <div className="m-trk">
          <div className="tk"><i className={pct >= 100 && c.format !== "up" ? "over" : ""} style={{ width: `${c.format === "up" ? 100 : pct}%` }} /></div>
          <div className="lb">
            <span>{mmss(total)} elapsed</span>
            <span>{c.format === "total" ? mmss(c.total * 60) : c.format === "per" ? `${mmss(sug)} for this problem` : "no limit"}</span>
          </div>
        </div>
        <div className="m-pn" aria-label="Problems">
          {round.ids.map((id, i) => {
            const m = round.marks[i];
            const cls = i === index && !logged ? "cur" : m ? (m.grade ? "done" : "skip") : i === index ? "cur" : "";
            return <span key={id} className={`m-pnum ${cls}`}>{i + 1}{m ? ` ${glyphOf(m.grade)}` : ""}</span>;
          })}
        </div>
        {!c.strict && <button className="m-ghost" onClick={togglePause}>{round.pausedAt == null ? "Pause" : "Resume"}</button>}
        {confirmEnd ? (
          <span className="p-save" style={{ gap: 8 }}>
            <button className="m-ghost" onClick={() => onFinish(round)}>End now</button>
            <button className="m-ghost" onClick={() => setConfirmEnd(false)}>Keep going</button>
          </span>
        ) : (
          <button className="m-ghost" onClick={() => setConfirmEnd(true)}>End round</button>
        )}
      </div>
      {banner && <div className="m-warn m-banner" role="status">{banner}</div>}
      {round.pausedAt != null && <div className="m-warn m-banner" role="status">Paused. The clock is stopped until you resume.</div>}

      <div className="wrap">
        <div className="p-grid">
          <div className="p-col">
            <section className="p-card">
              <span className="m-lab">PROBLEM {index + 1} OF {round.ids.length} · {DIFF[problem.difficulty][0].toUpperCase()} · SUGGESTED {Math.round(sug / 60)} MIN</span>
              <h3 className="m-ptitle">
                {showMeta ? `#${problem.number} ` : ""}{problem.title}
              </h3>
              <a className="m-open" href={leetcode(problem.slug)} target="_blank" rel="noopener noreferrer">Open on LeetCode ↗</a>
              <div className="m-ptime">
                <div className="tk"><i className={spent > sug ? "over" : ""} style={{ width: `${Math.min(100, (spent / Math.max(1, sug)) * 100)}%` }} /></div>
                <div className="lb">
                  <span>{mmss(spent)} on this problem</span>
                  <span>{mmss(sug)} suggested</span>
                </div>
              </div>
              {showMeta ? (
                <div className="m-meta">
                  <span>{patternName}</span>
                  {problem.tags.length > 0 && <span>{problem.tags.slice(0, 5).join(" · ")}</span>}
                  {problem.companies.length > 0 && <span>Asked by {problem.companies.slice(0, 4).map((x) => x.name).join(", ")}{problem.companies.length > 4 ? ` +${problem.companies.length - 4}` : ""}</span>}
                </div>
              ) : (
                <div className="m-blind"><b style={{ color: "var(--fg)" }}>Blind mode.</b> The number, topic, tags and companies are hidden until you log this problem. Open it on LeetCode, solve it there, then come back and say how it went.</div>
              )}
            </section>
            <section className="p-card" style={{ gap: 10 }}>
              <h2>THIS ROUND <em>{round.marks.filter((m) => m.grade).length} of {round.ids.length} logged</em></h2>
              <div className="m-stack">
                {round.ids.map((id, i) => {
                  const p = byId.get(id);
                  const m = round.marks[i];
                  const here = i === index;
                  const upcoming = i > index;
                  const took = m ? m.to - (round.starts[i] ?? 0) : null;
                  const tone = !m ? "" : m.grade === "again" ? "no" : m.grade === "hard" ? "half" : m.grade ? "ok" : "skip";
                  return (
                    <div key={id} className={`m-slot m-step${here ? " here" : ""}${upcoming ? " later" : ""}`}>
                      <span className="no">{i + 1}</span>
                      <span className="ti">
                        {upcoming || !p ? (
                          <>
                            <b className={`m-${p?.difficulty[0] ?? "m"}`} style={{ fontWeight: 600 }}>{p ? DIFF[p.difficulty][0] : "Problem"}</b> · hidden until you get there
                          </>
                        ) : here && !m && c.blind ? (
                          "Working on it now"
                        ) : (
                          <b style={{ fontWeight: 600, color: "var(--fg)" }}>{p.title}</b>
                        )}
                      </span>
                      <span className={`tm m-rs ${tone}`} style={{ fontSize: 12 }}>
                        {m ? (m.grade ? `${glyphOf(m.grade)} ${mmss(took ?? 0)}` : "skipped") : here ? "now" : `~${p ? Math.round(suggested(c, p.difficulty) / 60) : "?"}m`}
                      </span>
                    </div>
                  );
                })}
              </div>
            </section>
          </div>

          <aside className="p-col">
            <section className="p-card p-res">
              <h2>LOG PROBLEM {index + 1} <em>same as a normal attempt</em></h2>
              <div className="m-res3">
                {([["good", "✓", "on my own", "ok"], ["hard", "½", "with help", "half"], ["again", "✗", "not yet", "no"]] as const).map(([g, glyph, label, cls]) => (
                  <button key={g} className={`m-rb ${cls}${mark?.grade === g && logged ? " on" : ""}`} disabled={logged || busy} onClick={() => void log(g)}>
                    {glyph}<small>{label}</small>
                  </button>
                ))}
              </div>
              {error && <div className="m-bad">{error}</div>}
              {logged && mark && mark.grade && (
                <div className="m-logged">
                  Logged {glyphOf(mark.grade)}. {mark.due ? `Review ${niceDate(mark.due, data.today)}.` : "Practice problems schedule no reviews."}
                </div>
              )}
              <button className="m-go" disabled={!logged} onClick={next}>{lastOne ? "Finish the round →" : "Next problem →"}</button>
              {!logged && <button className="m-ghost" onClick={skip}>Skip this problem</button>}
              <p className="m-note">Logging stops this problem's clock and shows its topic. Skipping logs nothing, so it doesn't change your history or reviews.</p>
            </section>
          </aside>
        </div>
      </div>
    </>
  );
}

// ---------------------------------------------------------------- result

function Result({ data, round, onAgain, onChange }: { data: MockData; round: Round; onAgain: () => void; onChange: () => void }) {
  const byId = useMemo(() => new Map(data.problems.map((p) => [p.id, p])), [data.problems]);
  const c = round.config;
  const { items, seconds } = summary(round, 0);
  const own = items.filter((i) => i.grade === "good" || i.grade === "easy").length;
  const help = items.filter((i) => i.grade === "hard").length;
  const failed = items.filter((i) => i.grade === "again").length;
  const skipped = items.filter((i) => !i.grade).length;
  const pace = items.reduce((n, it) => n + suggested(c, byId.get(it.id)?.difficulty ?? "medium"), 0);
  const diff = seconds - pace;
  const spare = c.format === "total" ? c.total * 60 - seconds : null;
  const parts = [own ? `${own} solved on your own` : "", help ? `${help} with help` : "", failed ? `${failed} not yet` : "", skipped ? `${skipped} skipped` : ""].filter(Boolean);
  return (
    <div className="wrap" style={{ paddingBlock: 28 }}>
      <div className="eyebrow">
        <Link to="/dsa" style={{ color: "var(--ca)" }}>DSA</Link>
        <span>/</span>
        <span>MOCK INTERVIEW</span>
        <span>/</span>
        <span>ROUND FINISHED</span>
      </div>
      <h1 className="h1 md" style={{ fontSize: "clamp(30px,3.6vw,48px)" }}>
        {parts.length ? parts.join(", ") + "." : "Round ended."}{" "}
        {spare != null && <span style={{ color: "var(--acc)" }}>{spare >= 0 ? `Finished with ${mmss(spare)} to spare.` : `${mmss(-spare)} over the time.`}</span>}
      </h1>
      <p className="lead" style={{ marginTop: 12 }}>{describe(c, data)}</p>

      <div className="m-stats" style={{ marginTop: 24 }}>
        <div className="m-stat"><span className="k">TIME USED</span><span className="v">{mmss(seconds)}</span><span className="s">{c.format === "total" ? `of ${mmss(c.total * 60)}` : c.format === "per" ? "per-problem countdowns" : "stopwatch"}</span></div>
        <div className="m-stat"><span className="k">SOLVED ON MY OWN</span><span className="v">{own} / {items.length}</span><span className="s">{help} with help, {failed} not yet{skipped ? `, ${skipped} skipped` : ""}</span></div>
        <div className="m-stat"><span className="k">AGAINST SUGGESTED</span><span className="v" style={{ color: diff <= 0 ? "var(--grn)" : "var(--warn)" }}>{diff <= 0 ? "−" : "+"}{mmss(Math.abs(diff))}</span><span className="s">{mmss(pace)} suggested in all</span></div>
        <div className="m-stat"><span className="k">SETTINGS</span><span className="v" style={{ fontSize: 16, paddingTop: 6 }}>{c.strict ? "strict" : "pausable"} · {c.blind ? "blind" : "open"}</span><span className="s">{c.favour === "random" ? "uniform draw" : c.favour === "weak" ? "favoured weak ones" : "favoured often-asked"}</span></div>
      </div>

      <div className="m-tw" style={{ marginTop: 20 }}>
        <div className="m-tbl">
          <div className="m-tr th"><span>PROBLEM</span><span>RESULT</span><span>TIME</span><span>DIFFICULTY</span><span>WHAT HAPPENS NEXT</span></div>
          {items.map((it, i) => {
            const p = byId.get(it.id);
            if (!p) return null;
            const sug = suggested(c, p.difficulty);
            const cls = it.grade === "good" || it.grade === "easy" ? "ok" : it.grade === "hard" ? "half" : it.grade === "again" ? "no" : "skip";
            const mark = round.marks[i];
            const practice = p.lists.every((l) => l === "practice");
            return (
              <div key={it.id} className="m-tr">
                <div>
                  <a className="t1" href={leetcode(p.slug)} target="_blank" rel="noopener noreferrer">#{p.number} {p.title} ↗</a>
                  <span className="tags">{data.patterns.find((x) => x.code === p.pattern)?.name} · {p.tags.slice(0, 3).join(" · ")}{p.companies.length ? ` · ${p.companies.slice(0, 3).map((x) => x.name).join(", ")}` : ""}</span>
                </div>
                <span className={`m-rs ${cls}`}>{glyphOf(it.grade)}</span>
                <div className="m-tbar">
                  <div className="tk"><i className={it.seconds > sug ? "over" : ""} style={{ width: `${Math.min(100, (it.seconds / Math.max(1, sug)) * 100)}%` }} /></div>
                  <span>{it.seconds ? `${mmss(it.seconds)} of ${mmss(sug)}` : "not opened"}</span>
                </div>
                <span className={`m-${p.difficulty[0]}`}>{DIFF[p.difficulty][0]}</span>
                <span>{!it.grade ? "Not logged" : practice ? "No review (practice)" : mark?.due ? `Review ${niceDate(mark.due, data.today)}` : "Logged"}</span>
              </div>
            );
          })}
        </div>
      </div>

      <section className="p-card" style={{ marginTop: 20, gap: 10 }}>
        <h2>NEXT</h2>
        <div className="p-row">
          <button className="m-ghost" onClick={onAgain}>Another round, same settings</button>
          <button className="m-ghost" onClick={onChange}>Change settings</button>
        </div>
        <p className="m-note">Problems you logged ½ or ✗ become more likely when you choose "Favour my weak ones".</p>
      </section>
    </div>
  );
}
