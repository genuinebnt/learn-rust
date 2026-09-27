import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { marked } from "marked";
import { ApiError, api, type Diagnostic, type ProblemDetail, type RunOutcome, type RunView, type ScratchResult } from "../api";
import { Header } from "../components/Header";
import { BAND_LABEL, LEVEL_COLOR, Segs, modeColor, pad2 } from "../components/bits";
import { NAV_SECTIONS, SECTION_NAMES, type NavArea } from "../curriculum";
import { Editor } from "./Editor";
import { EditorSettingsButton } from "./EditorSettings";
import { useEditorSettings } from "../settings";
import { changedLines } from "./diff";
import { deriveLanes } from "./lanes";
import { type RaSession, type RaStatus, connectRa } from "./lsp";

type LeftTab = "problem" | "tests" | "hints" | "solution" | "related";
type ConsoleTab = "compiler" | "output" | "timeline";

const CONSOLE_MIN = 120;
const CONSOLE_BAR = 38;

/** Interview-realistic budgets from CURRICULUM.md, in minutes. */
const BUDGET = { write: { easy: 10, medium: 25, hard: 40 }, fix: { easy: 5, medium: 10, hard: 15 }, stage: { easy: 60, medium: 60, hard: 90 } } as const;

const md = (s: string) => marked.parse(s, { async: false });
const mmss = (s: number) => `${pad2(Math.floor(s / 60))}:${pad2(s % 60)}`;
const testNames = (src: string) => [...src.matchAll(/#\[test\]\s*(?:#\[[^\]]*\]\s*)*fn\s+(\w+)/g)].map((m) => m[1]!);
const areaOf = (section: string): NavArea => (Object.keys(NAV_SECTIONS) as NavArea[]).find((a) => (NAV_SECTIONS[a] as readonly string[]).includes(section)) ?? "dsa";

function runLabel(r: RunView): [string, string] {
  if (r.status !== "compile_error" && r.violations.length) return [`rule: ${r.violations[0]!.rule}`, "var(--warn)"];
  switch (r.status) {
    case "passed":
      return [`${r.passed} / ${r.total} ok`, "var(--grn)"];
    case "failed":
      return [`${r.passed} / ${r.total}`, "var(--acc)"];
    case "compile_error":
      return [r.diagnostics.find((d) => d.level === "error")?.code ?? "error", "var(--bad)"];
    case "timeout":
      return ["timeout", "var(--bad)"];
  }
}

export function Workspace({ id }: { id: string }) {
  const q = useQuery({ queryKey: ["problem", id], queryFn: () => api.problem(id) });
  if (!q.data) {
    return (
      <>
        <Header area="dsa" />
        <main className="page">
          <div className="wrap">
            <p className="notice">{q.isError ? `Couldn't load ${id}: ${(q.error as Error).message}` : "Loading…"}</p>
          </div>
        </main>
      </>
    );
  }
  return <Loaded key={id} p={q.data} />;
}

function Loaded({ p }: { p: ProblemDetail }) {
  const { editor: editorSettings } = useEditorSettings();
  useFocusHeartbeat(p.id);
  const qc = useQueryClient();
  const [code, setCode] = useState(p.draft ?? p.starter);
  const [docKey, setDocKey] = useState(`${p.id}:0`);
  const [left, setLeft] = useState<LeftTab>("problem");
  const [consoleTab, setConsoleTab] = useState<ConsoleTab>("compiler");
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [consoleH, setConsoleH] = useStoredNumber("anneal-console-height", 260);
  const [file, setFile] = useState<"lib" | "main" | "tests">("lib");
  const [main, setMain] = useState(p.scratch);
  const [scratchOut, setScratchOut] = useState<ScratchResult | null>(null);
  const [lastAction, setLastAction] = useState<"tests" | "scratch">("tests");
  const [autocomplete, setAutocomplete] = useState(true);
  const borrowish = p.mode === "fix" || p.tags.some((t) => /^E0[45]\d\d$/.test(t) || /borrow/.test(t));
  const [lanesOn, setLanesOn] = useState(borrowish);
  const [selected, setSelected] = useState<number | null>(null);
  const [open, setOpen] = useState<string | null>(null);
  const [cursor, setCursor] = useState([1, 1]);
  const [confirm, setConfirm] = useState<"reset" | "solution" | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [ra, setRa] = useState(true);
  const [raStatus, setRaStatus] = useState<RaStatus>("off");
  const [raDetail, setRaDetail] = useState<string | undefined>();
  const [raSession, setRaSession] = useState<RaSession | null>(null);
  const [raDiag, setRaDiag] = useState({ errors: 0, warnings: 0 });
  const [raEpoch, setRaEpoch] = useState(0);

  // rust-analyzer: one session per open problem, closed when toggled off or on leaving.
  useEffect(() => {
    if (!ra) {
      setRaStatus("off");
      return;
    }
    const session = connectRa(p.id, {
      status: (s, detail) => {
        setRaStatus(s);
        setRaDetail(detail);
        if (s === "ready") setRaEpoch((n) => n + 1);
      },
      diagnostics: (errors, warnings) => setRaDiag({ errors, warnings }),
    });
    session.ready.then(() => setRaSession(session), () => {});
    return () => {
      session.close();
      setRaSession(null);
      setRaDiag({ errors: 0, warnings: 0 });
    };
  }, [ra, p.id]);

  // Save to the server a second after typing stops so rust-analyzer's cargo check sees borrow errors.
  useEffect(() => {
    if (!raSession) return;
    const t = setTimeout(() => raSession.save(code), 1000);
    return () => clearTimeout(t);
  }, [code, raSession]);

  useEffect(() => {
    const start = Date.now();
    const t = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000);
    return () => clearInterval(t);
  }, []);

  // Autosave the buffer shortly after typing stops.
  const saved = useRef(code);
  useEffect(() => {
    if (code === saved.current) return;
    const t = setTimeout(() => {
      saved.current = code;
      api.saveDraft(p.id, code).catch(() => {});
    }, 800);
    return () => clearTimeout(t);
  }, [code, p.id]);

  // The scratch main.rs autosaves the same way.
  const savedMain = useRef(main);
  useEffect(() => {
    if (main === savedMain.current) return;
    const t = setTimeout(() => {
      savedMain.current = main;
      api.saveScratch(p.id, main).catch(() => {});
    }, 800);
    return () => clearTimeout(t);
  }, [main, p.id]);

  const showConsole = (tab: ConsoleTab) => {
    setConsoleTab(tab);
    setConsoleOpen(true);
  };
  const update = (next: ProblemDetail) => qc.setQueryData(["problem", p.id], next);
  const afterRun = (out: RunOutcome) => {
    qc.setQueryData<ProblemDetail>(["problem", p.id], (old) => old && { ...old, runs: [...old.runs, out.run], attempt: out.attempt, solution: out.solution });
    qc.invalidateQueries({ queryKey: ["tracks"] });
    qc.invalidateQueries({ queryKey: ["track"] });
    setSelected(null);
    setOpen(out.run.tests.find((t) => t.outcome !== "passed")?.name ?? null);
    setLastAction("tests");
    setLeft("tests");
    if (out.run.status === "compile_error") showConsole("compiler");
  };
  const run = useMutation({ mutationFn: () => api.run(p.id, code), onSuccess: afterRun });
  const submit = useMutation({ mutationFn: () => api.submit(p.id, code), onSuccess: afterRun });
  const hint = useMutation({ mutationFn: () => api.revealHint(p.id), onSuccess: update });
  const solution = useMutation({ mutationFn: () => api.revealSolution(p.id), onSuccess: (d) => (update(d), setConfirm(null)) });
  const reset = useMutation({
    mutationFn: () => api.reset(p.id),
    onSuccess: (d) => {
      update(d);
      saved.current = d.starter;
      setCode(d.starter);
      setDocKey(`${p.id}:${Date.now()}`);
      setConfirm(null);
    },
  });
  const scratch = useMutation({
    mutationFn: () => api.runScratch(p.id, code, main),
    onSuccess: (out) => {
      setScratchOut(out);
      setLastAction("scratch");
      showConsole(out.status === "compile_error" ? "compiler" : "output");
    },
  });
  const busy = run.isPending || submit.isPending || scratch.isPending;
  const doScratch = () => {
    if (busy || p.status !== "ready") return;
    showConsole("output");
    scratch.mutate();
  };
  const doRun = () => !busy && p.status === "ready" && run.mutate();
  const doSubmit = () => !busy && p.status === "ready" && submit.mutate();
  const failure = run.error ?? submit.error ?? scratch.error;

  const runs = p.runs;
  const latest = runs.at(-1);
  const shown = (selected !== null ? runs.find((r) => r.id === selected) : latest) ?? null;
  const shownIdx = shown ? runs.indexOf(shown) : -1;
  const prevRun = shownIdx > 0 ? runs[shownIdx - 1] : undefined;
  const lanes = useMemo(() => (latest ? deriveLanes(latest.diagnostics, latest.code) : null), [latest]);
  const lensDiags = useMemo(() => (latest && latest.code === code ? latest.diagnostics : latest?.diagnostics ?? []), [latest, code]);
  const names = useMemo(() => testNames(p.visible_tests), [p.visible_tests]);
  const budget = BUDGET[p.mode][p.level];
  const area = areaOf(p.track.section);

  return (
    <>
      <Header area={area} />
      <main>
        {p.attempt.resolve && (
          <div className="resolve-bar">
            <b>{p.attempt.solved ? "RE-SOLVED" : "RE-SOLVE"}</b>
            <span>
              {p.attempt.solved
                ? p.attempt.assisted
                  ? "Assisted this time: it comes back in 3 days."
                  : "Unassisted: it moves up the review ladder."
                : "From the starter, hints locked again. Solve it unassisted to move it up the review ladder."}
            </span>
          </div>
        )}
        <div className="subbar">
          <div className="crumb">
            <Link to={`/${area}`} style={{ color: modeColor(p.mode) }}>
              {SECTION_NAMES[p.track.section].toUpperCase()}
            </Link>
            <span>/</span>
            <Link to="/t/$track" params={{ track: p.track.slug }}>
              {p.track.code} {p.track.name.toUpperCase()}
            </Link>
            <span>/</span>
            <span>
              <span style={{ color: LEVEL_COLOR[p.stage.band] }}>{BAND_LABEL[p.stage.band]}</span> · {p.stage.name.toUpperCase()}
            </span>
          </div>
          <div className="vr" />
          <span className="wtitle">{p.title}</span>
          <div style={{ display: "flex", gap: 6 }}>
            <span className="pill solid" style={{ background: modeColor(p.mode) }}>
              {p.mode === "fix" ? "FIX THIS" : p.mode === "stage" ? "STAGE" : "WRITE IT"}
            </span>
            <span className="pill" style={{ borderColor: LEVEL_COLOR[p.level], color: LEVEL_COLOR[p.level] }}>
              {p.level.toUpperCase()}
            </span>
            {p.tags.slice(0, 3).map((t) => (
              <span className="pill" key={t}>
                {t}
              </span>
            ))}
          </div>
          <div className="sbr">
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              {p.prev ? (
                <Link to="/p/$id" params={{ id: p.prev }} style={{ color: "var(--dim)" }} aria-label="Previous problem">
                  ‹
                </Link>
              ) : (
                <span style={{ color: "var(--line)" }}>‹</span>
              )}
              <span>
                {p.position} / {p.count}
              </span>
              {p.next ? (
                <Link to="/p/$id" params={{ id: p.next }} style={{ color: "var(--dim)" }} aria-label="Next problem">
                  ›
                </Link>
              ) : (
                <span style={{ color: "var(--line)" }}>›</span>
              )}
            </div>
            <div className="clock" title={`Interview budget for a ${p.level} ${p.mode === "fix" ? "fix-this" : "problem"}: ${budget} minutes`}>
              <span className="dot" style={{ background: elapsed > budget * 60 ? "var(--bad)" : modeColor(p.mode) }} />
              <small>PRACTICE</small>
              <span style={{ color: "var(--fg)" }}>{mmss(elapsed)}</span>
              <small>/ {budget}:00</small>
            </div>
          </div>
        </div>

        <div className="ws">
          {/* ---------- left: problem, hints, solution ---------- */}
          <section className="pane l">
            <div className="tabs" role="tablist">
              {(
                [
                  ["problem", "Problem"],
                  ["tests", shown && shown.tests.length ? `Tests ${shown.passed}/${shown.total}` : "Tests"],
                  ["hints", `Hints ${p.hints.revealed.length}/${p.hints.total}`],
                  ["solution", "Solution"],
                  ["related", "Related"],
                ] as const
              ).map(([k, label]) => (
                <button key={k} role="tab" className={left === k ? "on" : ""} aria-selected={left === k} onClick={() => setLeft(k)}>
                  {label}
                </button>
              ))}
            </div>
            <div className="pbody">
              {left === "problem" && (
                <div className="stack">
                  <div className="lab">
                    {p.track.code} · {p.stage.name.toUpperCase()} · {p.stage.position} OF {p.stage.count}
                  </div>
                  <h2 className="ptitle">{p.title}</h2>
                  <div className="md" dangerouslySetInnerHTML={{ __html: md(p.statement) }} />
                  {p.rules && (
                    <div className="stack" style={{ gap: 8 }}>
                      <div className="lab">RULES</div>
                      <div className="rules" style={{ fontSize: 13.5, gridTemplateColumns: "14px 1fr", gap: "6px 8px" }}>
                        {p.rules.forbid_methods.map((m) => (
                          <Rule key={m} ok={false}>
                            no <code>.{m}()</code>
                          </Rule>
                        ))}
                        {p.rules.forbid_types.length > 0 && (
                          <Rule ok={false}>
                            no {p.rules.forbid_types.map((t, i) => (
                              <span key={t}>
                                {i > 0 && " / "}
                                <code>{t}</code>
                              </span>
                            ))}
                          </Rule>
                        )}
                        {p.rules.max_changed_lines !== null && <Rule ok>change at most {p.rules.max_changed_lines} lines</Rule>}
                      </div>
                      <p className="note">Checked on every run. A broken rule means a submit doesn't count, even when every test passes.</p>
                    </div>
                  )}
                  {p.examples.map((e, i) => (
                    <div className="stack" style={{ gap: 8 }} key={i}>
                      <div className="lab">EXAMPLE</div>
                      <div className="kv">
                        <span>input</span>
                        <code>{e.input}</code>
                        <span>returns</span>
                        <code style={{ color: "var(--grn)" }}>{e.output}</code>
                      </div>
                    </div>
                  ))}
                  {p.constraints.length > 0 && (
                    <div className="stack" style={{ gap: 8 }}>
                      <div className="lab">CONSTRAINTS</div>
                      <div className="m" style={{ fontSize: 12, lineHeight: 1.8 }}>
                        {p.constraints.map((c) => (
                          <div key={c}>{c}</div>
                        ))}
                      </div>
                    </div>
                  )}
                  {p.teaches.length > 0 && (
                    <div className="stack" style={{ gap: 10, paddingTop: 14, borderTop: "1px solid var(--line2)" }}>
                      <div className="lab">WHAT THIS TEACHES</div>
                      {p.teaches.map((t) => (
                        <div className="bul" key={t} style={{ ["--bul" as string]: modeColor(p.mode) }}>
                          <span className="md-inline" dangerouslySetInnerHTML={{ __html: marked.parseInline(t, { async: false }) }} />
                        </div>
                      ))}
                    </div>
                  )}
                  {p.follow_up && (
                    <div className="dash">
                      <div className="lab" style={{ color: "var(--acc)", marginBottom: 4 }}>
                        {p.mode === "fix" ? "ASKED AS" : "INTERVIEW FOLLOW-UP"}
                      </div>
                      {p.follow_up}
                    </div>
                  )}
                </div>
              )}

              {left === "tests" && (
                <div className="stack" style={{ gap: 14 }}>
                  {p.attempt.solved && (
                    <div className="solved">
                      <span className="lab" style={{ color: "var(--grn)" }}>
                        SOLVED{p.attempt.assisted ? " · ASSISTED" : ""}
                      </span>
                      {p.next ? (
                        <Link to="/p/$id" params={{ id: p.next }}>
                          Next problem →
                        </Link>
                      ) : (
                        <Link to="/t/$track" params={{ track: p.track.slug }}>
                          Back to {p.track.name} →
                        </Link>
                      )}
                    </div>
                  )}
                  <TestsPanel run={shown} names={names} busy={run.isPending || submit.isPending} open={open} setOpen={setOpen} runNo={shownIdx + 1} />
                </div>
              )}

              {left === "hints" && (
                <div className="stack" style={{ gap: 12 }}>
                  <p className="note">Each hint you open before solving marks the attempt as assisted and brings its re-solve date forward.</p>
                  {p.hints.revealed.map((h, i) => (
                    <div className="hint" key={i}>
                      <div className="lab" style={{ color: "var(--vio)", marginBottom: 6 }}>
                        HINT {i + 1} · {h.kind.toUpperCase()}
                      </div>
                      <div style={{ color: "var(--fg)" }}>{h.text}</div>
                    </div>
                  ))}
                  {p.hints.locked.length > 0 && (
                    <div className="hint lock">
                      <div className="lab" style={{ marginBottom: 6 }}>
                        HINT {p.hints.revealed.length + 1} · {p.hints.locked[0]!.toUpperCase()}
                      </div>
                      <button style={{ color: "var(--vio)" }} disabled={hint.isPending} onClick={() => hint.mutate()}>
                        {hint.isPending ? "Revealing…" : `Reveal hint ${p.hints.revealed.length + 1} →`}
                      </button>
                    </div>
                  )}
                  {p.hints.locked.length > 1 && <p className="note">{p.hints.locked.length - 1} more after this one.</p>}
                </div>
              )}

              {left === "solution" &&
                (p.solution.unlocked ? (
                  <div className="stack" style={{ gap: 14 }}>
                    <div className="lab" style={{ color: p.attempt.assisted ? "var(--warn)" : "var(--grn)" }}>
                      REFERENCE SOLUTION · {p.attempt.assisted ? "ASSISTED" : "UNLOCKED"}
                    </div>
                    <div className="solcode">
                      <Editor value={p.solution.code ?? ""} docKey={`${p.id}:solution`} readOnly />
                    </div>
                    {p.solution.notes && (
                      <>
                        <p style={{ margin: 0 }} dangerouslySetInnerHTML={{ __html: marked.parseInline(p.solution.notes.explanation, { async: false }) }} />
                        <div className="kv" style={{ padding: "12px 0", borderTop: "1px solid var(--line2)", borderBottom: "1px solid var(--line2)" }}>
                          <span>time</span>
                          <code>{p.solution.notes.time}</code>
                          <span>space</span>
                          <code>{p.solution.notes.space}</code>
                        </div>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="stack" style={{ gap: 12, padding: 18, border: "1px dashed var(--line)", borderRadius: 4 }}>
                    <div className="lab">LOCKED · {latest ? `${latest.passed} OF ${latest.total} TESTS PASSING` : "NOT RUN YET"}</div>
                    <div style={{ color: "var(--fg)" }}>The solution opens when every test passes on Submit.</div>
                    <div style={{ fontSize: 12.5 }}>Reveal it now and the attempt is marked assisted, with a re-solve in 3 days.</div>
                    {confirm === "solution" ? (
                      <div style={{ display: "flex", gap: 8 }}>
                        <button className="btn sm" style={{ borderColor: "var(--warn)", color: "var(--warn)" }} onClick={() => solution.mutate()} disabled={solution.isPending}>
                          Reveal and mark assisted
                        </button>
                        <button className="btn sm" onClick={() => setConfirm(null)}>
                          Keep trying
                        </button>
                      </div>
                    ) : (
                      <button className="btn sm" style={{ alignSelf: "flex-start" }} onClick={() => setConfirm("solution")}>
                        Reveal anyway
                      </button>
                    )}
                  </div>
                ))}

              {left === "related" && (
                <div className="stack" style={{ gap: 10 }}>
                  {p.related.length === 0 && <p className="note">No related tracks listed.</p>}
                  {p.related.map((code) => (
                    <div key={code} className="hint">
                      <span className="lab">{code}</span>
                      <br />
                      <span style={{ fontSize: 14, color: "var(--fg)" }}>{SECTION_NAMES[code[0] as keyof typeof SECTION_NAMES] ?? code}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* ---------- centre: editor, actions, console ---------- */}
          <section className="pane c">
            <div className="ftabs">
              <button className={`ftab${file === "lib" ? " on" : ""}`} onClick={() => setFile("lib")}>
                src/lib.rs
                {code !== (latest?.code ?? p.starter) && <span className="dot" style={{ background: "var(--mut)" }} title="Changed since the last test run" />}
              </button>
              <button className={`ftab${file === "main" ? " on" : ""}`} onClick={() => setFile("main")} title="Scratch main: Run builds and runs it">
                main.rs<small>SCRATCH</small>
              </button>
              <button className={`ftab${file === "tests" ? " on" : ""}`} onClick={() => setFile("tests")}>
                tests.rs<small>READ-ONLY</small>
              </button>
              <div className="tools">
                <EditorSettingsButton>
                  <Switch on={autocomplete} onClick={() => setAutocomplete(!autocomplete)} label="Autocomplete" />
                  <Switch on={ra} onClick={() => setRa(!ra)} label="rust-analyzer" />
                  {(borrowish || lanes) && <Switch on={lanesOn} onClick={() => setLanesOn(!lanesOn)} label="Borrow lanes" />}
                </EditorSettingsButton>
                {confirm === "reset" ? (
                  <span className="m" style={{ fontSize: 11, display: "flex", gap: 10 }}>
                    <button style={{ color: "var(--bad)" }} onClick={() => reset.mutate()}>
                      Reset to starter
                    </button>
                    <button style={{ color: "var(--dim)" }} onClick={() => setConfirm(null)}>
                      Cancel
                    </button>
                  </span>
                ) : (
                  <button className="m" style={{ fontSize: 11, color: "var(--dim)" }} onClick={() => setConfirm("reset")}>
                    Reset
                  </button>
                )}
                <span className="vr" style={{ height: 16 }} />
                <div className="wacts">
                  <button onClick={doScratch} disabled={busy || p.status !== "ready"} title="Build main.rs with your lib.rs and run it (⌘')">
                    {scratch.isPending ? "Running…" : "▷ Run"}
                  </button>
                  <button onClick={doRun} disabled={busy || p.status !== "ready"} title="Run the visible tests (⌘↵)">
                    {run.isPending ? "Testing…" : "Run tests"}
                  </button>
                  <button className="go" onClick={doSubmit} disabled={busy || p.status !== "ready"} title="Visible and hidden tests; passing solves it (⇧⌘↵)">
                    {submit.isPending ? "Submitting…" : "Submit"}
                  </button>
                </div>
              </div>
            </div>
            <div className="gbar">
              <div className="fp">
                <span style={{ color: "var(--fg)" }}>{file === "lib" ? "src/lib.rs" : file === "main" ? "src/bin/scratch.rs" : "tests/visible.rs"}</span>
                <span>edition 2021</span>
                <span>{p.crates.length ? `crates: ${p.crates.join(" · ")}` : "std only"}</span>
                <span>{file === "main" ? "⌘' runs it · tests don't run" : `${names.length} visible tests · hidden on Submit`}</span>
              </div>
              {lanesOn && file === "lib" && (
                <div className="lh">
                  <span>BORROW LANES</span>
                  <span style={{ color: lanes ? "var(--bad)" : "var(--grn)" }}>{lanes ? `${lanes.conflicts} CONFLICT${lanes.conflicts > 1 ? "S" : ""}` : "NO CONFLICTS"}</span>
                </div>
              )}
            </div>
            <div className="edit-host" hidden={file !== "lib"}>
              <Editor
                vim={editorSettings.vim}
                value={code}
                docKey={docKey}
                autocomplete={autocomplete}
                diagnostics={lensDiags}
                lanes={lanes}
                showLanes={lanesOn}
                lsp={raSession}
                lspEpoch={raEpoch}
                onChange={setCode}
                onCursor={(l, c) => setCursor([l, c])}
                onRun={doRun}
                onSubmit={doSubmit}
                onScratch={doScratch}
              />
            </div>
            <div className="edit-host" hidden={file !== "main"}>
              <Editor
                vim={editorSettings.vim}
                value={main}
                docKey={`${p.id}:main`}
                autocomplete={autocomplete}
                diagnostics={scratchOut && lastAction === "scratch" ? scratchOut.diagnostics.map(forScratch) : []}
                onChange={setMain}
                onCursor={(l, c) => setCursor([l, c])}
                onRun={doRun}
                onSubmit={doSubmit}
                onScratch={doScratch}
              />
            </div>
            {file === "tests" && (
              <div className="edit-host">
                <Editor value={p.visible_tests} docKey={`${p.id}:tests`} readOnly />
              </div>
            )}
            <div className="statusb">
              <RaStatusLine status={raStatus} detail={raDetail} errors={raDiag.errors} warnings={raDiag.warnings} />
              <span>autocomplete {autocomplete ? (raSession ? "on" : "on · buffer words") : "off"}</span>
              <span>
                Ln {cursor[0]}, Col {cursor[1]}
              </span>
              <span style={{ marginLeft: "auto" }}>rustc 1.98.1 stable · clippy on test runs · sandboxed</span>
            </div>
            <Console
              tab={consoleTab}
              setTab={(t) => showConsole(t)}
              open={consoleOpen}
              toggle={() => setConsoleOpen(!consoleOpen)}
              height={consoleH}
              setHeight={setConsoleH}
              summary={<ConsoleSummary busy={busy} scratchBusy={scratch.isPending} lastAction={lastAction} run={shown} scratch={scratchOut} />}
              errorCount={(lastAction === "scratch" ? scratchOut?.diagnostics : shown?.diagnostics)?.filter((d) => d.level === "error").length ?? 0}
            >
              {failure && <p className="notice bad" style={{ margin: "0 0 12px" }}>{failure instanceof ApiError ? failure.message : "The run failed to start. Is the API running?"}</p>}
              {consoleTab === "compiler" &&
                (lastAction === "scratch" && scratchOut ? (
                  <DiagnosticsList diagnostics={scratchOut.diagnostics} busy={scratch.isPending} empty="main.rs and lib.rs compiled cleanly." />
                ) : (
                  <CompilerPanel run={shown} busy={run.isPending || submit.isPending} />
                ))}
              {consoleTab === "output" && <OutputPanel run={shown} scratch={scratchOut} scratchBusy={scratch.isPending} />}
              {consoleTab === "timeline" && (
                <div className="tl" style={{ border: 0, padding: 0 }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    <div className="lab" style={{ letterSpacing: ".24em" }}>
                      RUN TIMELINE
                    </div>
                    <div className="runs">
                      {runs.length === 0 && <span className="note">No test runs yet. ⌘↵ runs the visible tests.</span>}
                      {runs.slice(-8).map((r) => {
                        const [label, color] = runLabel(r);
                        const on = shown?.id === r.id;
                        const squares = r.tests.length ? r.tests : names.map(() => null);
                        return (
                          <button key={r.id} className="run" style={{ borderColor: on ? color : "var(--line2)" }} onClick={() => setSelected(r.id)} title={`${r.kind} · ${new Date(r.created_at).toLocaleTimeString()}`}>
                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                              <span>#{runs.indexOf(r) + 1}</span>
                              <span style={{ color: "var(--dim)" }}>{r.kind === "submit" ? "sub" : new Date(r.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                            </div>
                            <div className="sq">
                              {squares.slice(0, 12).map((t, i) => (
                                <span key={i} style={{ background: t === null ? "var(--line2)" : t.outcome === "passed" ? "var(--grn)" : "var(--bad)" }} />
                              ))}
                            </div>
                            <span style={{ color }}>{label}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                  <div style={{ flex: 1, minWidth: 280, display: "flex", flexDirection: "column", gap: 10 }}>
                    <div className="lab" style={{ letterSpacing: ".24em" }}>
                      {shown && prevRun ? `DIFF · #${shownIdx} → #${shownIdx + 1}` : "DIFF"}
                    </div>
                    <div className="diff">
                      {shown && prevRun ? (
                        (() => {
                          const lines = changedLines(prevRun.code, shown.code);
                          return lines.length === 0 ? (
                            <span style={{ color: "var(--dim)" }}>No code changes between these runs.</span>
                          ) : (
                            lines.slice(0, 14).map((l, i) => (
                              <div key={i} style={{ color: l.op === "+" ? "var(--grn)" : "var(--bad)" }}>
                                {l.op} {l.text}
                              </div>
                            ))
                          );
                        })()
                      ) : (
                        <span style={{ color: "var(--dim)" }}>Two test runs are needed for a diff.</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </Console>
          </section>
        </div>
      </main>
    </>
  );
}

function RaStatusLine({ status, detail, errors, warnings }: { status: RaStatus; detail?: string; errors: number; warnings: number }) {
  const [text, color] =
    status === "off"
      ? ["rust-analyzer off · errors on run", "var(--line)"]
      : status === "connecting"
        ? ["rust-analyzer · starting…", "var(--dim)"]
        : status === "indexing"
          ? ["rust-analyzer · indexing…", "var(--acc)"]
          : status === "error"
            ? [`rust-analyzer unavailable${detail ? ` · ${detail}` : ""}`, "var(--bad)"]
            : [`rust-analyzer · ${errors} error${errors === 1 ? "" : "s"}${warnings ? ` · ${warnings} warning${warnings === 1 ? "" : "s"}` : ""}`, errors ? "var(--bad)" : "var(--grn)"];
  return (
    <span style={{ display: "flex", alignItems: "center", gap: 6 }} title={detail}>
      <span className="dot" style={{ background: color }} />
      {text}
    </span>
  );
}

function Rule({ ok, children }: { ok: boolean; children: React.ReactNode }) {
  return (
    <>
      <span style={{ color: ok ? "var(--grn)" : "var(--bad)" }}>{ok ? "+" : "×"}</span>
      <span>{children}</span>
    </>
  );
}

function Switch({ on, onClick, label, disabled, title }: { on: boolean; onClick?: () => void; label: string; disabled?: boolean; title?: string }) {
  return (
    <button className={`sw${on ? " on" : ""}`} onClick={onClick} aria-pressed={on} disabled={disabled} title={title} style={disabled ? { opacity: 0.5, cursor: "not-allowed" } : undefined}>
      <span className="tx">{label}</span>
      <span className="tr0" />
    </button>
  );
}

function TestsPanel({ run, names, busy, open, setOpen, runNo }: { run: RunView | null; names: string[]; busy: boolean; open: string | null; setOpen: (n: string | null) => void; runNo: number }) {
  if (busy)
    return (
      <div className="stack" style={{ gap: 14 }}>
        <div className="tsum">
          <b>Running…</b>
          <span>clippy → cargo test</span>
        </div>
        <Segs n={Math.max(names.length, 1)} filled={0} />
      </div>
    );
  if (!run)
    return (
      <div className="stack" style={{ gap: 14 }}>
        <div className="tsum">
          <b style={{ color: "var(--dim)" }}>Not run yet</b>
        </div>
        <div style={{ borderTop: "1px solid var(--line2)" }}>
          {names.map((n) => (
            <div className="trow" key={n} style={{ borderBottom: "1px solid var(--line2)" }}>
              <span className="sqr" style={{ background: "var(--line)" }} />
              <span className="nm" style={{ color: "var(--mut)" }}>
                {n}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  const summary =
    run.status === "compile_error"
      ? ["Doesn't compile", "var(--bad)"]
      : run.status === "timeout"
        ? ["Timed out", "var(--bad)"]
        : [`${run.passed} / ${run.total} passing`, run.status === "passed" ? "var(--grn)" : "var(--fg)"];
  const firstError = run.diagnostics.find((d) => d.level === "error");
  return (
    <div className="stack" style={{ gap: 14 }}>
      <div className="tsum">
        <b style={{ color: summary[1] }}>{summary[0]}</b>
        <span>
          {run.kind} #{runNo} · {(run.duration_ms / 1000).toFixed(1)}s
        </span>
      </div>
      {run.tests.length > 0 && (
        <div className="segs" style={{ gridTemplateColumns: `repeat(${run.tests.length}, 1fr)`, gap: 3, marginTop: 0 }}>
          {run.tests.map((t) => (
            <span key={t.suite + t.name} style={{ background: t.outcome === "passed" ? "var(--grn)" : "var(--bad)" }} />
          ))}
        </div>
      )}
      {run.violations.length > 0 && (
        <div className="rulebox">
          <span className="lab" style={{ color: "var(--warn)" }}>
            RULE BROKEN · {run.status === "passed" ? "TESTS PASS, BUT IT DOESN'T COUNT" : "FIX THE RULES TOO"}
          </span>
          {run.violations.map((v, i) => (
            <div key={i}>
              {v.line !== null && <span className="m">line {v.line} · </span>}
              {v.message}
            </div>
          ))}
        </div>
      )}
      {firstError && (
        <div className="errbox">
          <span className="lab" style={{ color: "var(--bad)" }}>
            {firstError.code ?? "ERROR"} · LINE {firstError.spans.find((s) => s.primary)?.line_start ?? "?"}
          </span>
          <br />
          {firstError.message}
        </div>
      )}
      {run.tests.length === 0 && (
        <div style={{ borderTop: "1px solid var(--line2)" }}>
          {names.map((n) => (
            <div className="trow" key={n} style={{ borderBottom: "1px solid var(--line2)" }}>
              <span className="sqr" style={{ background: "var(--line)" }} />
              <span className="nm" style={{ color: "var(--mut)" }}>
                {n}
              </span>
              <span className="tval">{run.status === "timeout" ? "timed out" : "not compiled"}</span>
            </div>
          ))}
        </div>
      )}
      <div style={{ borderTop: run.tests.length ? "1px solid var(--line2)" : undefined }}>
        {run.tests.map((t) => {
          const key = t.suite + t.name;
          const expanded = open === t.name && t.outcome !== "passed";
          const ok = t.outcome === "passed";
          return (
            <div key={key} style={{ borderBottom: "1px solid var(--line2)" }}>
              <button className="trow" onClick={() => setOpen(expanded ? null : t.name)}>
                <span className="sqr" style={{ background: ok ? "var(--grn)" : "var(--bad)" }} />
                <span className="nm" style={{ color: ok ? "var(--mut)" : "var(--fg)" }}>
                  {t.suite === "hidden" ? `hidden · ${t.name}` : t.name}
                </span>
                <span className="tval">{t.outcome === "timed_out" ? "timed out" : t.duration_ms !== null ? `${t.duration_ms.toFixed(1)} ms` : ""}</span>
              </button>
              {expanded && t.check && (
                <div className="tdet">
                  <span>input</span>
                  <span style={{ color: "var(--mut)" }}>{t.check.input}</span>
                  <span>expected</span>
                  <span style={{ color: "var(--grn)" }}>{t.check.expected}</span>
                  <span>got</span>
                  <span style={{ color: "var(--bad)" }}>{t.check.got}</span>
                </div>
              )}
              {expanded && !t.check && t.panic && <div className="tdet tpanic">{t.panic}</div>}
              {expanded && t.suite === "hidden" && <div className="note" style={{ margin: "-4px 0 12px 18px" }}>Hidden input. Often the same root cause as a visible failure.</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function CompilerPanel({ run, busy }: { run: RunView | null; busy: boolean }) {
  if (busy) return <p className="note">Compiling…</p>;
  if (!run) return <p className="note">Compiler and clippy output appears here after a run.</p>;
  return <DiagnosticsList diagnostics={run.diagnostics} busy={false} empty="Compiled cleanly. clippy found nothing." />;
}

function DiagnosticsList({ diagnostics, busy, empty }: { diagnostics: Diagnostic[]; busy: boolean; empty: string }) {
  if (busy) return <p className="note">Compiling…</p>;
  const errors = diagnostics.filter((d) => d.level === "error");
  const warnings = diagnostics.filter((d) => d.level !== "error");
  if (diagnostics.length === 0) return <p className="note">{empty}</p>;
  return (
    <div className="compiler">
      {[...errors, ...warnings].map((d, i) => (
        <pre key={i} className={d.level === "error" ? "err" : "warn"}>
          {d.rendered.trimEnd()}
        </pre>
      ))}
    </div>
  );
}

function OutputPanel({ run, scratch, scratchBusy }: { run: RunView | null; scratch: ScratchResult | null; scratchBusy: boolean }) {
  const printed = run?.tests.filter((t) => t.stdout) ?? [];
  return (
    <div className="compiler">
      <div className="lab" style={{ margin: "0 0 6px" }}>
        MAIN.RS{scratch && !scratchBusy ? ` · ${scratchStatus(scratch)} · ${(scratch.duration_ms / 1000).toFixed(1)}s` : ""}
      </div>
      {scratchBusy ? (
        <p className="note">Building and running main.rs…</p>
      ) : !scratch ? (
        <p className="note">Write a main in main.rs and press Run (⌘') to see its output here.</p>
      ) : scratch.status === "compile_error" ? (
        <p className="note">Didn't compile: see Compiler.</p>
      ) : (
        <>
          {scratch.stdout ? <pre className="out">{scratch.stdout}</pre> : <p className="note">No stdout.</p>}
          {scratch.stderr && <pre className="out err">{scratch.stderr}</pre>}
        </>
      )}
      <div className="lab" style={{ margin: "16px 0 6px" }}>
        TESTS
      </div>
      {printed.length === 0 ? (
        <p className="note">println!, eprintln! and dbg! output from the visible tests appears here after a test run, grouped by test. Hidden tests' output stays hidden.</p>
      ) : (
        printed.map((t) => (
          <div key={t.suite + t.name}>
            <div className="lab" style={{ margin: "10px 0 4px", color: t.outcome === "passed" ? "var(--grn)" : "var(--bad)" }}>
              {t.name}
            </div>
            <pre className="out">{t.stdout}</pre>
          </div>
        ))
      )}
    </div>
  );
}

const scratchStatus = (s: ScratchResult) =>
  s.status === "ok" ? "exit 0" : s.status === "exited" ? `exit ${s.exit_code ?? "?"}` : s.status === "timeout" ? "timed out" : "compile error";

/** Diagnostics from a scratch build point at src/bin/scratch.rs; the main.rs editor shows those only. */
function forScratch(d: Diagnostic): Diagnostic {
  return { ...d, spans: d.spans.filter((s) => s.file === "src/bin/scratch.rs").map((s) => ({ ...s, file: "src/lib.rs" })) };
}

function ConsoleSummary({ busy, scratchBusy, lastAction, run, scratch }: { busy: boolean; scratchBusy: boolean; lastAction: "tests" | "scratch"; run: RunView | null; scratch: ScratchResult | null }) {
  if (busy) return <span style={{ color: "var(--acc)" }}>{scratchBusy ? "running main.rs…" : "running tests…"}</span>;
  if (lastAction === "scratch" && scratch) {
    const ok = scratch.status === "ok";
    return <span style={{ color: ok ? "var(--grn)" : "var(--bad)" }}>main.rs · {scratchStatus(scratch)}</span>;
  }
  if (!run) return <span>no runs yet</span>;
  const [label, color] = runLabel(run);
  return <span style={{ color }}>{run.kind} · {label}</span>;
}

function Console({
  tab,
  setTab,
  open,
  toggle,
  height,
  setHeight,
  summary,
  errorCount,
  children,
}: {
  tab: ConsoleTab;
  setTab: (t: ConsoleTab) => void;
  open: boolean;
  toggle: () => void;
  height: number;
  setHeight: (h: number) => void;
  summary: React.ReactNode;
  errorCount: number;
  children: React.ReactNode;
}) {
  const drag = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!open) return;
    const startY = e.clientY;
    const startH = height;
    const pane = e.currentTarget.closest(".pane") as HTMLElement | null;
    const max = Math.max(CONSOLE_MIN, (pane?.clientHeight ?? 800) - 180);
    const move = (ev: PointerEvent) => setHeight(Math.min(max, Math.max(CONSOLE_MIN, startH + startY - ev.clientY)));
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      document.body.style.cursor = "";
    };
    document.body.style.cursor = "row-resize";
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  };
  return (
    <div className="console" style={{ height: open ? height : CONSOLE_BAR }}>
      <div className={`console-grip${open ? "" : " off"}`} onPointerDown={drag} aria-hidden="true" />
      <div className="console-bar">
        <div className="console-tabs" role="tablist">
          {(
            [
              ["compiler", errorCount ? `Compiler · ${errorCount}` : "Compiler"],
              ["output", "Output"],
              ["timeline", "Timeline"],
            ] as const
          ).map(([k, label]) => (
            <button key={k} role="tab" className={open && tab === k ? "on" : ""} aria-selected={open && tab === k} onClick={() => (open && tab === k ? toggle() : setTab(k))} style={k === "compiler" && errorCount ? { color: "var(--bad)" } : undefined}>
              {label}
            </button>
          ))}
        </div>
        <div className="console-sum">{summary}</div>
        <button className="console-toggle" onClick={toggle} aria-expanded={open} title={open ? "Hide the console" : "Show the console"}>
          {open ? "▾" : "▴"}
        </button>
      </div>
      {open && <div className="console-body">{children}</div>}
    </div>
  );
}

function useStoredNumber(key: string, initial: number): [number, (n: number) => void] {
  const [v, set] = useState(() => {
    try {
      const n = Number(localStorage.getItem(key));
      return Number.isFinite(n) && n > 0 ? n : initial;
    } catch {
      return initial;
    }
  });
  return [
    v,
    (n) => {
      set(n);
      try {
        localStorage.setItem(key, String(Math.round(n)));
      } catch {
        // Storage can be unavailable; the size still applies for this visit.
      }
    },
  ];
}

/** Reports active editing time: every 30 s while the tab is visible and you've typed or clicked in the last minute. */
function useFocusHeartbeat(id: string) {
  useEffect(() => {
    let last = Date.now();
    let active = Date.now();
    const mark = () => {
      active = Date.now();
    };
    window.addEventListener("keydown", mark);
    window.addEventListener("mousedown", mark);
    const timer = setInterval(() => {
      const now = Date.now();
      const seconds = Math.round((now - last) / 1000);
      last = now;
      if (document.visibilityState === "visible" && now - active < 60_000) api.focus(id, Math.min(seconds, 120)).catch(() => undefined);
    }, 30_000);
    return () => {
      clearInterval(timer);
      window.removeEventListener("keydown", mark);
      window.removeEventListener("mousedown", mark);
    };
  }, [id]);
}
