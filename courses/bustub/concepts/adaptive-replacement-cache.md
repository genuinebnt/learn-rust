---
title: ARC: a cache that tunes itself between recency and frequency
summary: The four lists of Megiddo and Modha's Adaptive Replacement Cache, how ghost hits move the target p, and the exact rules the stages test.
minutes: 12
---
LRU favours **recency**; LFU favours **frequency**. Which is right depends on the workload, and workloads change. **ARC** (Megiddo and Modha, FAST 2003) keeps both kinds of page in one cache and *learns* how to split the space between them from its own mistakes.

## The four lists

| list | holds | meaning |
|---|---|---|
| `mru` (T1 in the paper) | live pages seen **once** recently | the recency side |
| `mfu` (T2) | live pages seen **at least twice** | the frequency side |
| `mru_ghost` (B1) | page **ids** recently evicted from `mru` | no data, just the memory that they were here |
| `mfu_ghost` (B2) | page ids recently evicted from `mfu` | likewise |

The first two are real: their frames hold pages. The two **ghost lists** hold only identifiers, so they cost a few bytes per entry, and they are the whole trick: *a hit on a ghost is evidence that you evicted the wrong thing.*

Each list is ordered oldest to newest; eviction takes from the oldest end. A single number, the **target** `p` (here `mru_target_size`), says how many frames `mru` *should* hold; `mfu` should hold the other `c - p`, where `c` is the cache size.

```svg
caption: Two ghost lists and two live lists in one row, with the target p marking how much of the live space mru should have. A ghost hit moves p towards the side whose eviction was a mistake (the marker slides in the animation).
<svg viewBox="0 0 760 270" role="img" aria-label="Four lists mru_ghost, mru, mfu and mfu_ghost with a target marker between mru and mfu and arrows for the transitions">
<style>
@keyframes arc-p{0%,10%{transform:translateX(0)}40%,60%{transform:translateX(70px)}90%,100%{transform:translateX(0)}}
.arc-p{animation:arc-p 10s ease-in-out infinite}
</style>
<defs><marker id="arc-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="never" x="20" y="60" width="130" height="50" rx="4"/><text class="mid dim" x="85" y="82">mru_ghost</text><text class="mid dim sm" x="85" y="98">ids only</text>
<rect class="blue" x="160" y="60" width="210" height="50" rx="4"/><text class="mid t-b" x="265" y="82">mru</text><text class="mid dim sm" x="265" y="98">seen once</text>
<rect class="live" x="380" y="60" width="210" height="50" rx="4"/><text class="mid t-g" x="485" y="82">mfu</text><text class="mid dim sm" x="485" y="98">seen twice or more</text>
<rect class="never" x="600" y="60" width="140" height="50" rx="4"/><text class="mid dim" x="670" y="82">mfu_ghost</text><text class="mid dim sm" x="670" y="98">ids only</text>
<g class="arc-p"><line class="ln-w" x1="375" y1="46" x2="375" y2="124"/><text class="t-w sm" x="375" y="40" style="text-anchor:middle">target p</text></g>
<text class="dim sm" x="160" y="30">live frames (data)</text><text class="dim sm" x="20" y="30">ghosts</text>
<path class="ln" d="M265 150 V114" marker-end="url(#arc-a)"/><text class="dim sm" x="150" y="168">new page &#8594; mru</text>
<path class="ln-g" d="M300 190 C340 190 400 190 440 114" marker-end="url(#arc-a)"/><text class="t-g sm" x="240" y="206">hit in mru or mfu &#8594; newest end of mfu</text>
<path class="ln-b" d="M85 114 V130 H420 V114" marker-end="url(#arc-a)" style="stroke:var(--fn)"/><text class="t-b sm" x="30" y="146">ghost hit: p up</text>
<path class="ln-w" d="M670 114 V232 H500 V114" marker-end="url(#arc-a)"/><text class="t-w sm" x="520" y="250">ghost hit in mfu_ghost: p down</text>
<text class="dim sm" x="30" y="250">eviction: the oldest evictable frame becomes a ghost</text>
</svg>
```

## The rules (the variant these stages test)

**A page is accessed:**

1. **It is live (a hit in `mru` or `mfu`)**: move it to the newest end of `mfu`. It has now been seen twice.
2. **It is a ghost in `mru_ghost`**: *recency was undervalued.* Increase `p` (more room for `mru`) by `1`, or by `|mfu_ghost| / |mru_ghost|` if `mfu_ghost` is the larger list (integer division). Remove the ghost; the page re-enters as live in `mfu`.
3. **It is a ghost in `mfu_ghost`**: *frequency was undervalued.* Decrease `p` by `1`, or by `|mru_ghost| / |mfu_ghost|` if `mru_ghost` is larger, never below 0. Remove the ghost; the page re-enters in `mfu`.
4. **It is new**: make room in the *ghost* lists first, so the whole structure stays bounded (below), then add it to the newest end of `mru`.

**A frame is evicted:** if `|mru| >= p`, take the oldest *evictable* frame in `mru`; otherwise take it from `mfu`. If the chosen list has no evictable frame, use the other one. The victim's page id becomes a ghost in the matching ghost list.

Notice how the learning works. If `mru` keeps losing pages that are wanted again (hits in `mru_ghost`), `p` grows, `mru` is protected, and eviction moves to `mfu`. If the workload is a scan, pages are touched once, never reach `mfu`, and fall out of `mru` as ghosts that are never hit; `p` stays low and the frequent pages in `mfu` survive.

## Bounds, so the ghosts cannot grow without end

ARC's invariants (paper, with `c` the cache size):

- `|mru| + |mru_ghost| <= c`
- `|mru| + |mfu| + |mru_ghost| + |mfu_ghost| <= 2c`

When a new page arrives and the first bound would break, drop the oldest `mru_ghost`; otherwise if the second would, drop the oldest `mfu_ghost`. So the metadata is at most twice the cache and old history ages out.

## Compared with LRU-K

| | LRU-K | ARC |
|---|---|---|
| tunable parameter | `K` (chosen by you) | none: `p` is learned |
| extra memory | K timestamps per page | ghost ids (up to `c`) |
| scan-resistant | yes | yes |
| adapts to a change of workload | slowly (history of K accesses) | quickly (every ghost hit moves `p`) |
| complexity | an ordered set | four lists and two hash maps, O(1) per operation |
| patent | none | IBM patented ARC; PostgreSQL briefly used it and then moved to other policies |

> [!NOTE] BusTub's version
> BusTub's description differs from the paper in details (the ghost-hit step sizes and the list-maintenance on a miss); this course follows BusTub's, and the stage tests pin each rule.
