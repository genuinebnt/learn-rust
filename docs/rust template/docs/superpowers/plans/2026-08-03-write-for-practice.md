# Write for Practice (W3 + W4 + W5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add **Write for practice** with three clusters (W3 Mini Rc, W4 Bounded Queue, W5 Thread Pool) — 8 different domain problems each (24 total), prompt + starter only, no solution keys.

**Architecture:** New `part-practice.html` loaded via `index.html` `load()`. Sidebar section after Write from scratch with three topic clusters. Cards reuse existing CSS. Future W* groups append the same pattern.

**Tech Stack:** Static HTML study packet (no Cargo). Serve folder over local HTTP for `fetch()`.

## Global Constraints

- Prompt + starter only — **no** `<details>`, probe lists, or senior-angle blocks
- Each card cues its source W* (“Practice on W3/W4/W5 …”)
- Stay inside that exercise’s concept budget (see spec) — no cross-contamination (e.g. no Condvar in W5 cards; no channels in W4 cards; no Arc/Weak in W3 cards)
- IDs: `prac-w3-1`…`prac-w3-8`, `prac-w4-1`…`prac-w4-8`, `prac-w5-1`…`prac-w5-8`
- Display P1–P8 **per cluster** with `(W3)` / `(W4)` / `(W5)` in sidebar labels
- Paths under `rust template/` relative to repo root `interview_templates/`
- Spec: `rust template/docs/superpowers/specs/2026-08-03-write-for-practice-design.md`

## File map

| File | Role |
|------|------|
| Create: `rust template/part-practice.html` | Header + 3 topic notes + 24 cards |
| Modify: `rust template/index.html` | Sidebar + footer counts (~353 → ~377) |

---

### Task 1: Scaffold page header + topic notes

**Files:**
- Create: `rust template/part-practice.html`

- [ ] **Step 1: Write scaffold**

```html
<!-- ═══════════════════════════════════════════
     PART: WRITE FOR PRACTICE
     Solo muscle-memory drills — prompt + starter only (no solution keys)
═══════════════════════════════════════════ -->

<div class="page-header" id="practice-header">
  <div class="ph-eyebrow">Write for Practice · Muscle Memory</div>
  <div class="ph-title">Write for Practice</div>
  <div class="ph-sub">
    Different problems on topics you already met in <strong>Write from scratch</strong>.
    No solution keys here — rewrite the machinery cold until it sticks.
    If you peeked at a W* solution, use these so a differently worded interview question
    on the same topic still feels natural. Stuck? Revisit the matching Write-from-scratch
    exercise, then come back and retry without looking.
  </div>
  <div class="ph-badges">
    <span class="badge badge-time">24 drills · W3 · W4 · W5</span>
    <span class="badge badge-time">Prompt + starter only</span>
    <span class="badge badge-time">More groups as you finish more W*</span>
  </div>
</div>
```

Then three topic anchors (notes only — cards come in later tasks):

```html
<div class="note" id="practice-w3" style="margin-bottom:32px;">
  <strong>W3 · Mini Rc&lt;T&gt; practice.</strong>
  Same concepts every time (refcount, <code>Clone</code>/<code>Deref</code>/<code>Drop</code>,
  <code>NonNull</code> + heap free at zero) — different domain wording.
  Single-threaded only; no <code>Weak</code>, no atomics/<code>Arc</code>.
</div>

<div class="note" id="practice-w4" style="margin-bottom:32px;">
  <strong>W4 · Bounded Blocking Queue practice.</strong>
  Same concepts every time (<code>Mutex</code> + <code>Condvar</code>, capacity,
  block on full/empty, <code>while</code> wait loops) — different domain wording.
  No channels; no close/shutdown broadcast.
</div>

<div class="note" id="practice-w5" style="margin-bottom:32px;">
  <strong>W5 · Thread Pool practice.</strong>
  Same concepts every time (fixed workers, shared channel, type-erased jobs,
  lock-then-run, clean <code>Drop</code>) — different domain wording.
  No result handles, no Condvar queues, no bounded <code>sync_channel</code>.
</div>
```

- [ ] **Step 2: Verify**

```bash
test -f "rust template/part-practice.html"
rg -n "details|solution key|probe-list" "rust template/part-practice.html" || echo "OK"
```

- [ ] **Step 3: Commit**

```bash
git add "rust template/part-practice.html"
git commit -m "$(cat <<'EOF'
Add Write for practice page header and W3/W4/W5 topic notes.

EOF
)"
```

---

### Task 2: W3 practice cards (prac-w3-1 … prac-w3-8)

**Files:**
- Modify: `rust template/part-practice.html` — insert **after** `#practice-w3` note and **before** `#practice-w4` note

**Concept budget:** MiniRc-shaped API: `new`, `clone`, `Deref`, `Drop`, `strong_count`; `NonNull`; `Box::leak`/`from_raw` pair; single-threaded.

- [ ] **Step 1: Insert eight W3 cards**

Use bar/eyebrow color `var(--c-smart)`. Each prompt starts with `Practice on <strong>W3 · Mini Rc</strong>.` Starter pattern (rename type per card):

```rust
use std::ops::Deref;
use std::ptr::NonNull;

struct Inner<T> { value: T, count: usize }
struct SharedConfig<T> { ptr: NonNull<Inner<T>> }  // name changes per card

impl<T> SharedConfig<T> {
    fn new(value: T) -> Self {
        let boxed = Box::new(Inner { value, count: 1 });
        Self { ptr: NonNull::from(Box::leak(boxed)) }
    }
    // TODO: clone, Deref, Drop, strong_count
}
```

| ID | Title | Type name | Prompt domain (one sentence) |
|----|--------|-----------|------------------------------|
| prac-w3-1 | Shared Config Handle | `SharedConfig<T>` | Refcounted config shared across modules |
| prac-w3-2 | Shared String Buffer | `SharedBuf<T>` | Multiple owners of one heap value |
| prac-w3-3 | Scene Mesh Handle | `MeshHandle<T>` | Render nodes share one mesh allocation |
| prac-w3-4 | Shared AST Node | `AstRc<T>` | Parser nodes share a sub-expression |
| prac-w3-5 | Shared Image Pixels | `PixRc<T>` | UI widgets share one pixel buffer |
| prac-w3-6 | Playlist Metadata | `MetaRc<T>` | Tracks share album metadata |
| prac-w3-7 | Shared Stylesheet | `StyleRc<T>` | Nodes share one style object |
| prac-w3-8 | Cold Rewrite SharedBox | `SharedBox<T>` | Blank-page MiniRc under a new name |

Match write-from-scratch HTML span classes (`kw`, `ty`, `fn`, `cm`, `nm`, `lt`). Include a tiny `main` stub only on prac-w3-1 and prac-w3-8 (optional); others can be API-only like most W cards.

Full HTML card skeleton (repeat 8× with table substitutions):

```html
<div class="section" id="prac-w3-1">
  <div class="section-header">
    <div class="sh-bar" style="background:var(--c-smart)"></div>
    <div>
      <div class="sh-eyebrow" style="color:var(--c-smart)">// Practice · W3 Mini Rc · ~25 min</div>
      <div class="sh-title">P1 · Shared Config Handle</div>
    </div>
  </div>
  <div class="card">
    <div class="ex-meta">
      <span class="chip">W3 practice</span>
      <span class="chip">unsafe</span>
      <span class="chip">Deref</span>
      <span class="chip chip-hard">Hard</span>
    </div>
    <div class="card-label"><span class="cl-pip" style="background:var(--c-smart)"></span>Prompt</div>
    <div class="note">Practice on <strong>W3 · Mini Rc</strong>. …</div>
    <div class="card-label" style="margin-top:16px;"><span class="cl-pip" style="background:var(--text-dim)"></span>Starter code</div>
<pre>…</pre>
  </div>
</div>
```

- [ ] **Step 2: Verify**

```bash
rg -n 'id="prac-w3-[1-8]"' "rust template/part-practice.html"
rg -n 'std::rc::Rc|AtomicUsize|Weak|Arc<' "rust template/part-practice.html" || echo "OK: no out-of-scope W3 APIs in file yet (re-check after all tasks)"
```

After this task, W3 cards must not mention `Weak`/`Arc`/`Atomic` as required APIs.

- [ ] **Step 3: Commit**

```bash
git add "rust template/part-practice.html"
git commit -m "$(cat <<'EOF'
Add Write for practice W3 Mini Rc drills (8 problems).

EOF
)"
```

---

### Task 3: W4 practice cards (prac-w4-1 … prac-w4-8)

**Files:**
- Modify: `rust template/part-practice.html` — insert after `#practice-w4` note, before `#practice-w5`

**Concept budget:** `Mutex` + `Condvar`, fixed capacity, blocking `push`/`pop`, `while` waits, no channels.

- [ ] **Step 1: Insert eight W4 cards**

Bar color `var(--c-thr)`. Prompt prefix: `Practice on <strong>W4 · Bounded Blocking Queue</strong>.`

Starter pattern (rename type per card):

```rust
use std::collections::VecDeque;
use std::sync::{Condvar, Mutex};

struct PrinterQueue<T> {
    capacity: usize,
    // TODO: mutex-protected queue + condvars
}

impl<T> PrinterQueue<T> {
    fn new(capacity: usize) -> Self { todo!() }
    fn push(&self, item: T) { /* blocks while full */ }
    fn pop(&self) -> T { /* blocks while empty */ }
}
```

| ID | Title | Type name |
|----|--------|-----------|
| prac-w4-1 | Printer Job Queue | `PrinterQueue<T>` |
| prac-w4-2 | Download Slot Queue | `DownloadQueue<T>` |
| prac-w4-3 | Audio Block Queue | `AudioQueue<T>` |
| prac-w4-4 | Order Window | `OrderWindow<T>` |
| prac-w4-5 | Upload Buffer | `UploadBuffer<T>` |
| prac-w4-6 | Chat Fan-in Buffer | `ChatBuffer<T>` |
| prac-w4-7 | Worker Mailbox | `Mailbox<T>` |
| prac-w4-8 | Cold Rewrite BoundedBuffer | `BoundedBuffer<T>` |

Emphasize in at least prac-w4-1 and prac-w4-8 prompts: `while` not `if` around waits; no `mpsc`.

- [ ] **Step 2: Verify**

```bash
rg -n 'id="prac-w4-[1-8]"' "rust template/part-practice.html"
rg -n 'mpsc|sync_channel' "rust template/part-practice.html" | rg 'prac-w4' || echo "OK: no channels in W4 section"
```

- [ ] **Step 3: Commit**

```bash
git add "rust template/part-practice.html"
git commit -m "$(cat <<'EOF'
Add Write for practice W4 bounded-queue drills (8 problems).

EOF
)"
```

---

### Task 4: W5 practice cards (prac-w5-1 … prac-w5-8)

**Files:**
- Modify: `rust template/part-practice.html` — append after `#practice-w5` note

**Concept budget:** W5 thread pool only (see spec).

- [ ] **Step 1: Insert eight W5 cards**

IDs `prac-w5-1`…`prac-w5-8`. Titles/domains from spec (ImagePool, HashPool, HandlerPool, MailPool, LogPool, ThumbPool, MapPool, JobRunner with `submit`).

Use the same full card HTML previously planned for P1–P8, but:

- `id="prac-w5-N"` (not `pN`)
- Eyebrow: `// Practice · W5 Thread Pool · ~25 min`
- Chip: `W5 practice`
- Every prompt: `Practice on <strong>W5 · Thread Pool</strong>.`

Starters (abbreviated — expand to highlighted HTML like W5 write card):

| ID | Type | Key methods |
|----|------|-------------|
| prac-w5-1 | `ImagePool` | `new`, `execute`, `Drop` |
| prac-w5-2 | `HashPool` | same; emphasize `Arc<Mutex<Receiver>>` |
| prac-w5-3 | `HandlerPool` | same; `type Job = Box<dyn FnOnce() + Send + 'static>` |
| prac-w5-4 | `MailPool` | `Worker` + `Option<JoinHandle>` hint |
| prac-w5-5 | `LogPool` | comment: lock → recv → unlock → job() |
| prac-w5-6 | `ThumbPool` | `execute(&self, …)` |
| prac-w5-7 | `MapPool` | no result channel |
| prac-w5-8 | `JobRunner` | `submit` instead of `execute` |

- [ ] **Step 2: Verify whole file**

```bash
rg -n 'id="prac-w[345]-[1-8]"' "rust template/part-practice.html" | wc -l
rg -n 'details|Full solution|probe-list' "rust template/part-practice.html" || echo "OK: no solution keys"
rg -c 'W3 ·|W4 ·|W5 ·' "rust template/part-practice.html"
```

Expected: 24 section ids; OK on solution keys; multiple W* cues.

- [ ] **Step 3: Commit**

```bash
git add "rust template/part-practice.html"
git commit -m "$(cat <<'EOF'
Add Write for practice W5 thread-pool drills (8 problems).

EOF
)"
```

---

### Task 5: Wire sidebar + progress counts

**Files:**
- Modify: `rust template/index.html`

- [ ] **Step 1: Insert sidebar after Write from scratch, before Debrief**

```html
  <div class="sb-section">
    <div class="sb-section-label">Write for practice</div>
    <div class="sb-link" onclick="load('part-practice.html','practice-header')"><span class="sb-pip" style="background:var(--c-async)"></span>Overview</div>

    <div class="sb-link" onclick="load('part-practice.html','practice-w3')"><span class="sb-pip" style="background:var(--c-smart)"></span>W3 · Mini Rc practice</div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-1')"><span class="sb-pip" style="background:var(--c-smart)"></span>P1 · Shared config (W3)<span class="sb-check" data-id="prac-w3-1" onclick="toggleDone(event,'prac-w3-1')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-2')"><span class="sb-pip" style="background:var(--c-smart)"></span>P2 · Shared string buf (W3)<span class="sb-check" data-id="prac-w3-2" onclick="toggleDone(event,'prac-w3-2')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-3')"><span class="sb-pip" style="background:var(--c-smart)"></span>P3 · Scene mesh (W3)<span class="sb-check" data-id="prac-w3-3" onclick="toggleDone(event,'prac-w3-3')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-4')"><span class="sb-pip" style="background:var(--c-smart)"></span>P4 · Shared AST (W3)<span class="sb-check" data-id="prac-w3-4" onclick="toggleDone(event,'prac-w3-4')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-5')"><span class="sb-pip" style="background:var(--c-smart)"></span>P5 · Shared pixels (W3)<span class="sb-check" data-id="prac-w3-5" onclick="toggleDone(event,'prac-w3-5')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-6')"><span class="sb-pip" style="background:var(--c-smart)"></span>P6 · Playlist meta (W3)<span class="sb-check" data-id="prac-w3-6" onclick="toggleDone(event,'prac-w3-6')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-7')"><span class="sb-pip" style="background:var(--c-smart)"></span>P7 · Shared style (W3)<span class="sb-check" data-id="prac-w3-7" onclick="toggleDone(event,'prac-w3-7')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w3-8')"><span class="sb-pip" style="background:var(--c-smart)"></span>P8 · SharedBox cold (W3)<span class="sb-check" data-id="prac-w3-8" onclick="toggleDone(event,'prac-w3-8')"></span></div>

    <div class="sb-link" onclick="load('part-practice.html','practice-w4')"><span class="sb-pip" style="background:var(--c-thr)"></span>W4 · Bounded queue practice</div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-1')"><span class="sb-pip" style="background:var(--c-thr)"></span>P1 · Printer queue (W4)<span class="sb-check" data-id="prac-w4-1" onclick="toggleDone(event,'prac-w4-1')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-2')"><span class="sb-pip" style="background:var(--c-thr)"></span>P2 · Download slots (W4)<span class="sb-check" data-id="prac-w4-2" onclick="toggleDone(event,'prac-w4-2')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-3')"><span class="sb-pip" style="background:var(--c-thr)"></span>P3 · Audio blocks (W4)<span class="sb-check" data-id="prac-w4-3" onclick="toggleDone(event,'prac-w4-3')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-4')"><span class="sb-pip" style="background:var(--c-thr)"></span>P4 · Order window (W4)<span class="sb-check" data-id="prac-w4-4" onclick="toggleDone(event,'prac-w4-4')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-5')"><span class="sb-pip" style="background:var(--c-thr)"></span>P5 · Upload buffer (W4)<span class="sb-check" data-id="prac-w4-5" onclick="toggleDone(event,'prac-w4-5')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-6')"><span class="sb-pip" style="background:var(--c-thr)"></span>P6 · Chat buffer (W4)<span class="sb-check" data-id="prac-w4-6" onclick="toggleDone(event,'prac-w4-6')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-7')"><span class="sb-pip" style="background:var(--c-thr)"></span>P7 · Worker mailbox (W4)<span class="sb-check" data-id="prac-w4-7" onclick="toggleDone(event,'prac-w4-7')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w4-8')"><span class="sb-pip" style="background:var(--c-thr)"></span>P8 · BoundedBuffer cold (W4)<span class="sb-check" data-id="prac-w4-8" onclick="toggleDone(event,'prac-w4-8')"></span></div>

    <div class="sb-link" onclick="load('part-practice.html','practice-w5')"><span class="sb-pip" style="background:var(--c-async)"></span>W5 · Thread pool practice</div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-1')"><span class="sb-pip" style="background:var(--c-async)"></span>P1 · Image-resize pool (W5)<span class="sb-check" data-id="prac-w5-1" onclick="toggleDone(event,'prac-w5-1')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-2')"><span class="sb-pip" style="background:var(--c-thr)"></span>P2 · File hasher pool (W5)<span class="sb-check" data-id="prac-w5-2" onclick="toggleDone(event,'prac-w5-2')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-3')"><span class="sb-pip" style="background:var(--c-async)"></span>P3 · HTTP handler pool (W5)<span class="sb-check" data-id="prac-w5-3" onclick="toggleDone(event,'prac-w5-3')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-4')"><span class="sb-pip" style="background:var(--c-thr)"></span>P4 · Email sender pool (W5)<span class="sb-check" data-id="prac-w5-4" onclick="toggleDone(event,'prac-w5-4')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-5')"><span class="sb-pip" style="background:var(--c-async)"></span>P5 · Log-shipping pool (W5)<span class="sb-check" data-id="prac-w5-5" onclick="toggleDone(event,'prac-w5-5')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-6')"><span class="sb-pip" style="background:var(--c-thr)"></span>P6 · Thumbnail pool (W5)<span class="sb-check" data-id="prac-w5-6" onclick="toggleDone(event,'prac-w5-6')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-7')"><span class="sb-pip" style="background:var(--c-async)"></span>P7 · Map-step pool (W5)<span class="sb-check" data-id="prac-w5-7" onclick="toggleDone(event,'prac-w5-7')"></span></div>
    <div class="sb-link" onclick="load('part-practice.html','prac-w5-8')"><span class="sb-pip" style="background:var(--c-thr)"></span>P8 · Cron job runner (W5)<span class="sb-check" data-id="prac-w5-8" onclick="toggleDone(event,'prac-w5-8')"></span></div>
  </div>
```

- [ ] **Step 2: Bump counts**

Replace hardcoded `353` with `377` in footer + welcome badge. Footer line example:

`98 write · 24 practice · 75 blind75 · ~377 trackable items`

- [ ] **Step 3: Smoke test**

```bash
cd "rust template" && python3 -m http.server 8765
```

Open overview, one W3 card, one W4 card, one W5 card — confirm prompt+starter, no reveal UI.

- [ ] **Step 4: Commit**

```bash
git add "rust template/index.html" "rust template/part-practice.html"
git commit -m "$(cat <<'EOF'
Wire Write for practice (W3/W4/W5) into the sidebar.

EOF
)"
```

---

### Task 6: Commit updated spec + plan

**Files:**
- Modify (already edited): spec + this plan

- [ ] **Step 1: Commit docs**

```bash
git add \
  "rust template/docs/superpowers/specs/2026-08-03-write-for-practice-design.md" \
  "rust template/docs/superpowers/plans/2026-08-03-write-for-practice.md"
git commit -m "$(cat <<'EOF'
Expand Write for practice design/plan to W3, W4, and W5.

EOF
)"
```

---

## Spec coverage

| Requirement | Task |
|-------------|------|
| W3 × 8 | 2 |
| W4 × 8 | 3 |
| W5 × 8 | 4 |
| Header + topic notes | 1 |
| Sidebar + counts | 5 |
| No solution keys | verified each content task |
| Concept budgets isolated | task 2–4 verify steps |
| Docs updated | 6 |
