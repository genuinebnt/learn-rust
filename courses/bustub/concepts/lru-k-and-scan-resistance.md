---
title: LRU-K: backward k-distance and scan resistance
summary: The idea in the 1993 LRU-K paper, how to read backward k-distance, why one extra bit of history defeats the sequential scan, and the tie-break the stages test.
minutes: 9
---
LRU judges a page by one number: when it was last used. That one number cannot tell a page used a thousand times from a page used once, and a sequential scan is nothing but pages used once. **LRU-K** (O'Neil, O'Neil and Weikum, SIGMOD 1993) remembers the last **K** uses of every page and judges by the K-th most recent one.

## Backward k-distance

At time *t*, the **backward k-distance** of a page is *how far back its K-th most recent access was*. A page with fewer than K recorded accesses has **infinite** backward k-distance. LRU-K evicts the page with the **largest** backward k-distance.

For K = 2, with the access history (time → frame): `t0:A t1:B t2:A t3:C t4:B`, evaluated at t = 5:

| frame | accesses | 2nd most recent | backward 2-distance |
|---|---|---|---|
| A | t0, t2 | t0 | 5 - 0 = 5 |
| B | t1, t4 | t1 | 5 - 1 = 4 |
| C | t3 only | none | **infinity** |

C has been used once, so it goes first. Between A and B, A's second-most-recent use is older, so A goes next. Plain LRU would have evicted A first too, but for a different reason (last used at t2, the oldest), and the two policies diverge as soon as a hot page and a scanned page have the same recency.

```svg
caption: Backward 2-distances at t = 5. C was used once, so its distance is infinite and it is evicted first; between A and B the larger distance (A, whose second most recent use is oldest) goes next.
<svg viewBox="0 0 760 230" role="img" aria-label="A timeline of accesses to frames A, B and C and their backward 2-distances">
<line class="grid" x1="40" y1="130" x2="720" y2="130"/>
<text class="dim sm" x="40" y="26">time &#8594;</text>
<g>
<circle class="box" cx="80" cy="130" r="20"/><text class="mid fg" x="80" y="135">A</text><text class="mid dim sm" x="80" y="166">t0</text>
<circle class="box" cx="200" cy="130" r="20"/><text class="mid fg" x="200" y="135">B</text><text class="mid dim sm" x="200" y="166">t1</text>
<circle class="box" cx="320" cy="130" r="20"/><text class="mid fg" x="320" y="135">A</text><text class="mid dim sm" x="320" y="166">t2</text>
<circle class="hot" cx="440" cy="130" r="20"/><text class="mid t-a" x="440" y="135">C</text><text class="mid dim sm" x="440" y="166">t3</text>
<circle class="box" cx="560" cy="130" r="20"/><text class="mid fg" x="560" y="135">B</text><text class="mid dim sm" x="560" y="166">t4</text>
<line class="ln-w dash" x1="660" y1="50" x2="660" y2="190"/><text class="t-w sm" x="668" y="46">now (t5)</text>
</g>
<path class="ln-b" d="M80 100 V70 H660" /><text class="t-b sm" x="90" y="64">A: 2nd most recent is t0, distance 5</text>
<path class="ln-b" d="M200 100 V88 H660" /><text class="t-b sm" x="210" y="82">B: 2nd most recent is t1, distance 4</text>
<text class="t-a sm" x="440" y="200">C: one access: distance infinity: evicted first</text>
</svg>
```

## Why it resists scans

A scan touches each of a million pages **once**, so each scanned page has fewer than 2 accesses and infinite distance. A hot page touched twice or more has a *finite* distance. Eviction always prefers infinite to finite, so scanned pages leave before hot ones, however recently the scan touched them. Under LRU the scan flushes the pool; under LRU-2 the hot set survives.

## The tie-break among infinite distances

Many pages can have infinite distance at once (every one-touch page). The paper says to break ties by plain LRU among them, and BusTub specifies it as: **among frames with fewer than K accesses, evict the one whose earliest recorded access is oldest.** A frame with K or more accesses is ordered by its K-th most recent access (older is larger). That gives a total order; add the frame id as a last tie-break and it is deterministic.

```rust
fn eviction_key(node: &LruKNode) -> (u8, usize, FrameId) {
    match node.kth_timestamp() {
        None    => (0, node.first_timestamp().unwrap_or(0), node.fid),   // infinite: first, oldest first access first
        Some(t) => (1, t, node.fid),                                      // finite: after them, oldest k-th access first
    }
}
```

The smallest key is the next victim: a tuple compares lexicographically, so `0` sorts before `1`.

## What to remember about the history

Only the **last K** timestamps matter, so each node keeps a `VecDeque<usize>` and pops the front when it grows past K. Memory is O(K) per frame, not O(accesses). The paper adds a refinement, the **correlated reference period** (ignore re-references within a short window, so a burst of accesses by one transaction counts once); BusTub does not require it.

## Choosing K

| K | behaviour |
|---|---|
| 1 | exactly LRU |
| 2 | the usual choice: distinguishes "once" from "more than once", little memory, adapts quickly |
| large | slower to adapt to a change of working set; remembers more |

> [!NOTE] What LRU-K does not fix
> A page referenced twice by a scan (a join that revisits a block) looks hot. And LRU-K's tuning knob K is fixed: ARC (module 1e) adapts to the workload without one.
