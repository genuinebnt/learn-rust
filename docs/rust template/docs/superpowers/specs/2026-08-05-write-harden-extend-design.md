# Write-from-Scratch · Harden / Extend Sub-Problems — Design Spec

**Date:** 2026-08-05  
**Status:** Implemented for W1–W98  
**Scope:** All write-from-scratch exercises (Batch 1 curated W1–W10; W11–W98 derived from each exercise’s senior probes/signals)

## Goal

Under each Write-from-scratch exercise, add **Harden / extend** sub-problems that deepen the *same* problem family (new methods, improvements, edge APIs) — not “different problems on the same topic” (that is Write for practice).

Format: **prompt + starter only** — no solution keys, no compile harness.

## Value filter (every sub must pass)

Include a sub only if it forces at least one of:

1. **A judgment call** you under-trained in the core W* (lifetimes, ordering, lock scope, uniqueness, spurious wakeups, …)
2. **A real API edge** of the same type in std/production (`get_mut` if unique, `try_push`, `close`, `peek` without LRU promote, …)
3. **A failure mode** of the original design (panic in worker, shutdown races, off-by-one windows, error `source` chains)

**Reject:** trivial getters (`capacity()` alone), renames, or busywork that doesn’t change how you think about the topic.

## Distinction

| Track | Intent |
|-------|--------|
| Write from scratch (main) | Interview-shaped core exercise + solution key |
| **Harden / extend** (this) | Extend/improve that same artifact |
| Write for practice | Different problems using the same *concepts/tools* |

## UX (nested under each `#wN`)

After the main card’s solution/`insight`, still inside the `#wN` section:

1. Divider: **Harden / extend · same problem family**
2. One-line note: prompt + starter only; no solution key; builds on the W* above
3. 4–5 sub-cards with IDs `wN-x1` … `wN-x5`
4. Each sub-card: title, chips, prompt `note`, starter `pre` (same syntax spans as write)
5. **No** `<details>` solutions, probes, or senior-angle blocks on subs

Sidebar: keep a single link per W* (no 5× nav spam). Extensions appear when opening that W*.

## Batching

Topic-order waves of ~10 W* each. This spec’s implementation target is **Batch 1 = W1–W10**.

## Batch 1 extension catalog (4–5 each) — value-focused

Each line: **what you build** — *why it hardens the W* topic*.

### W1 · Stack\<T\> (ownership / borrowing on a collection)
1. **`peek_mut`** — mutable borrow of top without pop; forces `&mut self` vs `&self` discipline  
2. **`iter` / `iter_mut`** — expose stack contents without moving; lifetime tied to `&self`  
3. **`IntoIterator` for `&Stack` / `&mut Stack`** — same idea as std collections; solidifies borrowing iterators  
4. **`drain`** — emptying while yielding owned `T`; Drop/partial-drain thinking  
5. **`FromIterator` + `Extend`** — build/extend from iterators (how stacks show up in real APIs)

### W2 · Thread-safe counter (atomics vs mutex, ordering)
1. **CAS loop: increment only if `< max`** — `compare_exchange` until success; real atomic pattern beyond `fetch_add`  
2. **Ordering drill** — shared “ready” flag + counter: when Relaxed is wrong and Acquire/Release is needed  
3. **Mutex multi-field update** — `{count, last_tid}` under one lock; when atomics stop being enough  
4. **Join-timing bugfix** — rewrite a broken “join inside spawn loop” version; concurrency structure, not API trivia  
5. **`fetch_update`-style max** — implement “store max of current and x” with CAS (composes atomic skill)

### W3 · MiniRc (refcount invariants / unsafe discipline)
1. **`get_mut` if unique** — only if `count == 1`; uniqueness is the core Rc insight  
2. **`try_unwrap`** — recover `T` iff last handle; ownership transfer out of the Rc  
3. **`into_raw` / `from_raw`** — leak/reconstitute count ownership; same invariant as Drop, different path  
4. **`ptr_eq`** — identity vs value equality; how shared ownership is observed  
5. **Double-free / early-free bug hunt** — given a broken Drop (wrong decrement order), fix it; etches the invariant

### W4 · Bounded blocking queue (Condvar correctness)
1. **`try_push` / `try_pop`** — non-blocking API; same state machine without waiting  
2. **`close()` + unblock waiters** — the #1 real follow-up; `notify_all`, closed flag in `while` conditions  
3. **`wait_timeout` push/pop** — timed Condvar; same pattern, harder control flow  
4. **Spurious-wakeup hardening** — rewrite a buggy `if` wait as correct `while`; the W4 senior signal  
5. **Single condvar vs two** — implement with one condvar + `notify_all`; trade-offs vs `not_full`/`not_empty`

### W5 · Thread pool (queue, workers, shutdown)
1. **`execute` → oneshot result** — return a receiver/future-like handle per job; natural extension of fire-and-forget  
2. **`catch_unwind` in workers** — panicking job must not kill the pool; production pool reality  
3. **Shutdown race: `try_execute` after drop started** — state around sender/`Option`  
4. **Lock-scope bugfix** — broken worker that holds mutex across `job()`; fix it (the W5 footgun)  
5. **Bounded job channel (`sync_channel`)** — backpressure on `execute`; composes queue thinking into the pool

### W6 · Plugin logger (trait objects / dyn composition)
1. **Levels + filter on the trait/facade** — `dyn Logger` still works; policy vs sink separation  
2. **Broadcast / tee sink** — one facade, N `Box<dyn Logger>`; object-safety + ownership of sinks  
3. **`flush` on the trait** — object-safe method design; when default methods help  
4. **Swap/replace sink at runtime** — `Box<dyn Logger>` behind `Mutex` or replace on `&mut self`  
5. **Prefixing adapter** — wrapper `Logger` that decorates another; decorator pattern with trait objects

### W7 · Treiber stack (lock-free CAS)
1. **Correct `Drop` draining the list** — no leaks; ownership of nodes after pop loop  
2. **`pop` ABA discussion-as-code** — tagged pointer or document why toy Treiber ignores ABA; hardens lock-free literacy  
3. **Drain into `Vec`** — empty stack safely under concurrency assumptions (single-threaded drain after quiesce, or pop-loop)  
4. **`is_empty` via atomic load** — relaxed vs acquire when reading top  
5. **`push`/`pop` memory ordering audit** — justify each `Ordering`; the real Treiber learning

### W8 · LRU cache (structure + eviction policy)
1. **`peek` without promoting** — policy vs lookup; classic LRU interview follow-up  
2. **`get_mut` + promote** — mutable access still updates recency  
3. **`resize` / shrink capacity** — evict until within new cap; eviction loop correctness  
4. **Iterate oldest → newest** — proves the list/map invariant  
5. **O(1) vs O(n) honesty** — if core used `Vec` for order, upgrade link structure *or* document cost and fix one path

### W9 · Sliding-window iterator (Iterator + slices)
1. **Strided windows** — `size` + `step`; generalizes `pos += 1` (your list)  
2. **Zero-alloc `trim_slice`** — return `&[T]` sub-slice by value trimming; lifetime skill next to windows  
3. **Group-by iterator** — custom `Iterator` over runs; same `next()` muscle, new state machine  
4. **In-place slice rotate** — `&mut [T]` algorithm fluency tied to slice thinking (your list)  
5. **Non-overlapping `chunks`** — sibling of windows; boundary/`size_hint` practice

### W10 · Custom error + `?` (error composability)
1. **`source()` chain** — `Error::source` to wrapped I/O; real debugging contract  
2. **Multiple `From` impls** — `io::Error`, `ParseIntError`, … into one enum; `?` ergonomics  
3. **`context(msg)` / `with_context`** — attach path/op without losing source  
4. **`Display` vs `Debug` discipline** — user-facing vs programmer-facing messages  
5. **Fallible iterator / map_err boundary** — convert foreign errors at API edge into your type

## Implementation touchpoints

- Modify: `rust template/part-write.html` (append harden blocks inside W1–W10 sections)
- Optional: tiny CSS in `index.html` only if divider needs a class (prefer existing `.note` / `.card`)
- No Cargo / no solutions
- Docs: this spec; plan per batch as needed

## Success criteria (Batch 1)

- Each of W1–W10 has 4–5 harden subs with starter stubs and no solution `<details>`
- Copy makes “extends this W*” obvious
- W9 includes the user’s four named problems plus `chunks`
- Pattern reusable for Batch 2 (W11–W20)

## Non-goals

- Solutions for harden subs  
- Sidebar link per sub-problem  
- Mixing these into Write for practice  
- Completing W11–W98 in Batch 1
