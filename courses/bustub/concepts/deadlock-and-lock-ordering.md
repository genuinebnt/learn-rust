---
title: Deadlock, lock ordering and holding a lock while you wait
summary: The four conditions of a deadlock, how page latches plus a pool lock produce one, the flush bug the stages teach, and the rules (order, short sections, never wait while holding) that remove it.
minutes: 9
---
A **deadlock** is a set of threads each holding something another needs and waiting for something another holds. The system is not slow or busy; it is stopped, and no timeout or error will say why. The buffer pool has exactly the ingredients (a global lock, per-page latches, a blocking disk wait), and the last stage of module 1g is about a bug where they combine.

## The four conditions (Coffman, 1971)

A deadlock needs **all four**; remove any one and it cannot happen:

1. **Mutual exclusion**: a resource is held by one thread at a time (a mutex, a write latch).
2. **Hold and wait**: a thread holds one resource while waiting for another.
3. **No preemption**: a resource cannot be taken away; its holder must release it.
4. **Circular wait**: there is a cycle of threads, each waiting for the next one's resource.

You cannot remove (1) or (3) for locks. The practical levers are (2) *do not wait while holding* and (4) *impose a global order so no cycle can form*.

## The flush bug

```text
thread A: holds the WRITE latch of page 7 (a WritePageGuard) and asks the pool for another page: it needs the pool lock
thread B: flush_page(7):  takes the POOL lock, then waits for page 7's read latch to copy the bytes
```

A holds the page latch and needs the pool lock. B holds the pool lock and needs the page latch. Neither can proceed: a cycle. It needs only one writer and one flusher on the same page, so it passes every single-threaded test and appears under load.

```svg
caption: Thread A holds page 7's write latch and waits for the pool lock; thread B holds the pool lock and waits for page 7's latch. The arrows form a cycle, so neither can ever continue. Pinning first and releasing the pool lock breaks the cycle.
<svg viewBox="0 0 760 240" role="img" aria-label="A wait cycle between two threads, a pool lock and a page latch">
<defs><marker id="dl-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--bad)"/></marker><marker id="dl-b" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="blue" x="60" y="40" width="170" height="50" rx="6"/><text class="mid t-b" x="145" y="62">thread A</text><text class="mid dim sm" x="145" y="80">writer; wants another page</text>
<rect class="blue" x="530" y="150" width="170" height="50" rx="6"/><text class="mid t-b" x="615" y="172">thread B</text><text class="mid dim sm" x="615" y="190">flush_page(7)</text>
<rect class="hot" x="530" y="40" width="170" height="50" rx="6"/><text class="mid t-a" x="615" y="62">pool lock</text><text class="mid dim sm" x="615" y="80">protects the metadata</text>
<rect class="live" x="60" y="150" width="170" height="50" rx="6"/><text class="mid t-g" x="145" y="172">page 7 write latch</text><text class="mid dim sm" x="145" y="190">the page's bytes</text>
<path class="ln" d="M145 150 V92" marker-end="url(#dl-b)"/><text class="dim sm" x="152" y="124">A holds</text>
<path class="ln" d="M615 92 V148" marker-end="url(#dl-b)"/><text class="dim sm" x="622" y="124">B holds</text>
<path class="ln-w" d="M232 58 H528" marker-end="url(#dl-a)" style="stroke:var(--bad)"/><text class="t-r sm" x="300" y="50">A waits for the pool lock</text>
<path class="ln-w" d="M528 182 H232" marker-end="url(#dl-a)" style="stroke:var(--bad)"/><text class="t-r sm" x="300" y="206">B waits for the page latch</text>
</svg>
```

## The fix: do not hold the pool lock while waiting for the latch

```rust
let frame = {
    let mut inner = self.inner.lock().unwrap();                 // pool lock
    let Some(&frame) = inner.page_table.get(&page_id) else { return false };
    inner.meta[frame.0].pin_count += 1;                         // PIN the page: it cannot be evicted now
    inner.replacer.set_evictable(frame, false);
    frame
};                                                              // pool lock released HERE
let copy = /* wait for the frame's read latch, copy the bytes */;
self.write_page_data(page_id, &copy);
self.unpin_page(page_id, false);                                // pool lock again, briefly
```

The **pin** stands in for the lock: it promises the frame will not be reused, so the pool lock can be released *before* the potentially long wait for the latch. That removes "hold and wait" for the pair (pool lock, page latch).

## Rules that prevent deadlock

| rule | removes | example here |
|---|---|---|
| **a fixed lock order** (pool lock before page latch, parent page before child, left before right) | circular wait | a thread never takes the pool lock while holding a page latch it then waits on |
| **never block while holding a lock someone else needs** (disk I/O, another lock, a channel `get`) | hold and wait | release the pool lock before waiting for the latch |
| **keep critical sections short** and lexically scoped (a guard's lifetime) | makes both easier to see | `{ let mut inner = lock(); ...; }` |
| **try-lock and back off** | hold and wait (by giving up) | `try_write()` and retry |
| **a timeout that reports** | detection, not prevention | the stage tests wait on futures with a deadline and fail with a message |

> [!TIP] Finding one
> A hung test is a deadlock until proven otherwise. On macOS or Linux, `sample <pid>` / `gdb -p <pid> -batch -ex "thread apply all bt"` prints every thread's stack; look for two threads each inside `lock()` or `read()`/`write()`, and read the frames above to see what each already holds.

## Deadlock detection (a preview)

Module 4's lock manager cannot always order its locks (transactions choose their own), so it **detects** deadlocks instead: build a *waits-for graph* (an edge from each waiting transaction to the one holding what it wants) and abort a transaction on a cycle. The same four conditions, a different lever.
