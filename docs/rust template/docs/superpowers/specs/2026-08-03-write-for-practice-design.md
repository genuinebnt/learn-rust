# Write for Practice — Design Spec

**Date:** 2026-08-03  
**Status:** Approved design; scope expanded to W3 + W4 + W5  
**Scope (this batch):** Three practice groups — W3 Mini Rc, W4 Bounded Blocking Queue, W5 Thread Pool

## Goal

Add a **Write for practice** section: lean write-yourself drills with **prompt + starter stubs only** (no solution keys, no probes, no compiling harness).

Purpose: after learning a Write-from-scratch exercise (even if the solution was peeked), reframe the same concepts as different problems so the machinery becomes muscle memory. An interviewer can ask a differently worded question on the same topic and the answer is still there.

This is not for introducing new concepts. New practice groups are added later as more W* exercises are learned.

## Relationship to Write from scratch

| | Write from scratch | Write for practice |
|--|--------------------|--------------------|
| Audience | Interviewer reference + deep study | Solo recall / muscle memory |
| Content | Prompt, starter, full solution, probes, insight | Prompt + starter only |
| This batch | W3, W4, W5 (sources of truth) | 8 different problems per topic (24 total) |

Every card cues its source exercise (e.g. “Practice on W3 · Mini Rc”).

## Packaging (Approach A)

- New file: `part-practice.html` (same `load()` pattern as other parts)
- Sidebar section **after** “Write from scratch”, label: `Write for practice`
- Three topic clusters in sidebar + page (order matches learning progression): **W3 → W4 → W5**
- IDs: `prac-w3-1`…`prac-w3-8`, `prac-w4-1`…`prac-w4-8`, `prac-w5-1`…`prac-w5-8`
- Display titles reuse P1–P8 **within each cluster**, always with a `(W3)` / `(W4)` / `(W5)` cue
- Checkboxes via `sb-check` / `toggleDone` on those `data-id`s
- Future W* groups append the same way

## Card UX

- Page header: study-mode copy — no solution keys; if stuck, revisit matching W* then retry cold
- Topic intro notes before each cluster (one short note per W3 / W4 / W5)
- Per card: eyebrow, title, chips, prompt `note`, starter `pre` with `todo!()` / TODO stubs
- Colors: W3 `--c-smart`; W4 `--c-thr`; W5 `--c-async` / `--c-thr`
- **Omit:** `<details>` solution keys, probe lists, senior-angle insight blocks

## Concept budgets (do not expand beyond the source W*)

### W3 · Mini Rc\<T\>

**In scope:** single-threaded refcounted handle; `NonNull` + heap allocation (`Box::leak` / `Box::from_raw` or equivalent pair); `Clone` increments count; `Deref` to `T`; `Drop` decrements then frees at 0; `strong_count`; `unsafe` with clear invariants; not using `std::rc::Rc` internally.

**Out of scope:** `Weak`, `Arc`/atomics, `Send`/`Sync` impls, custom allocators.

### W4 · Bounded blocking queue

**In scope:** fixed capacity; `Mutex` + `Condvar` (no channels); `push` blocks while full; `pop` blocks while empty; `while` wait loops (spurious wakeups); re-assign guard from `wait`; typically two condvars (`not_full` / `not_empty`); `notify_one` on the ordinary path; `VecDeque` (or equivalent) behind the mutex.

**Out of scope:** `close()`/shutdown broadcast, `mpsc`/`sync_channel`, timeouts, async queues.

### W5 · Thread pool

**In scope:** fixed N workers; `mpsc` job queue; `Arc<Mutex<Receiver>>`; `Box<dyn FnOnce() + Send + 'static>`; `execute(&self, …)` (or same-shaped rename); drop lock before running job; Drop via take-sender + join; `Option` + `take` as needed.

**Out of scope:** result/`JoinHandle`-like returns (W34), bounded `sync_channel` backpressure, Condvar queues (W4), panic restart, work-stealing, Tokio.

## Problem sets

### W3 practice (P1–P8)

| ID | Title | Domain framing |
|----|--------|----------------|
| prac-w3-1 | Shared config handle | Refcounted app `Config` shared across modules |
| prac-w3-2 | Shared string buffer | Multiple owners of one heap `String` |
| prac-w3-3 | Scene mesh handle | Render nodes share one mesh allocation |
| prac-w3-4 | Shared AST node | Parser nodes share a sub-expression |
| prac-w3-5 | Shared image pixels | UI widgets share one pixel buffer |
| prac-w3-6 | Playlist metadata | Tracks share album metadata blob |
| prac-w3-7 | Shared stylesheet | DOM-like nodes share one style object |
| prac-w3-8 | Cold rewrite `SharedBox` | Blank-page MiniRc under a new name |

### W4 practice (P1–P8)

| ID | Title | Domain framing |
|----|--------|----------------|
| prac-w4-1 | Printer job queue | Bounded print-job buffer; block when full/empty |
| prac-w4-2 | Download slot queue | Cap concurrent download descriptors |
| prac-w4-3 | Audio block queue | Producer/consumer audio blocks, fixed capacity |
| prac-w4-4 | Order window | Kitchen order tickets, capacity N |
| prac-w4-5 | Upload buffer | Bounded pending uploads |
| prac-w4-6 | Chat fan-in buffer | Bounded inbound messages |
| prac-w4-7 | Worker mailbox | Bounded tasks for a single worker thread |
| prac-w4-8 | Cold rewrite `BoundedBuffer` | Blank-page queue under a new name |

### W5 practice (P1–P8)

| ID | Title | Domain framing |
|----|--------|----------------|
| prac-w5-1 | Image-resize worker pool | N workers run resize closures |
| prac-w5-2 | Parallel file hasher | Workers pull path jobs from a shared channel |
| prac-w5-3 | Sync HTTP request handler pool | Per-connection type-erased jobs |
| prac-w5-4 | Batch email sender | Fire-and-forget send tasks |
| prac-w5-5 | Log-shipping pool | Lock only for `recv`, then run I/O job |
| prac-w5-6 | Thumbnail generator | Pool shared across threads; `execute(&self)` |
| prac-w5-7 | Fixed-worker map step | Side-effect jobs; no result channel |
| prac-w5-8 | Cron-style job runner | Cold rewrite; scheduler-shaped names |

## Implementation touchpoints

1. Create `rust template/part-practice.html` — header + W3/W4/W5 clusters (24 cards)
2. Wire sidebar in `rust template/index.html` after Write from scratch
3. Bump trackable footer (~353 → ~377 = +24)
4. No Cargo/test harness

## Success criteria

- Sidebar loads all three clusters; each card is prompt + starter only
- Every card cues its W* source; problems stay inside that W* concept budget
- Pattern stays obvious for adding future practice groups after more W* topics

## Non-goals

- Compiling or judging solutions
- Cross-contaminating concept budgets across W3/W4/W5
- Merging practice into `part-write.html`
