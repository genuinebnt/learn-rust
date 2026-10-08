---
title: Replacement policies: LRU, CLOCK, OPT and what a good cache looks like
summary: What a page replacement policy decides, why recency is a good guess, how LRU, FIFO and CLOCK differ on one reference string, and the anomaly that makes FIFO unusable.
minutes: 10
---
A buffer pool holds a few thousand pages in memory out of millions on disk. When a page not in memory is needed and every frame is full, something must go. A **replacement policy** chooses what. The choice decides how often you wait for the disk, which is most of a database's run time.

## The goal and the ideal

The goal is to maximise the **hit ratio**: the fraction of accesses served from memory. The impossible ideal is **OPT** (Belady's algorithm, 1966): evict the page whose *next* use is farthest in the future. It needs to see the future, so no system can run it, but it is the yardstick every real policy is measured against.

Real policies guess the future from the past, relying on **locality**: pages used recently are likely to be used again soon (temporal locality), and pages near one another tend to be used together.

| policy | evicts | bookkeeping | cost per access |
|---|---|---|---|
| **FIFO** | the page that has been resident longest | a queue | O(1) |
| **LRU** | the page not used for the longest time | a list + a map (move to back on use) | O(1) with handles |
| **CLOCK** | an approximation of LRU: a page not used since the hand last passed | a ring, one bit per page | O(1) amortised, no list updates on a hit |
| **LRU-K / ARC** | LRU refined to resist scans / adapt to the workload | more lists | modules 1d and 1e |
| **OPT** | the page used farthest in the future | the future | impossible |

## One reference string, three policies

Reference string `1 2 3 4 1 2 5 1 2 3 4 5` (twelve accesses, five distinct pages). Counting **faults** (misses) with 3 and with 4 frames:

| policy | 3 frames | 4 frames |
|---|---|---|
| FIFO | 9 | **10** |
| LRU | 10 | 8 |
| OPT | 7 | 6 |

Two things stand out. LRU is within a couple of OPT's faults here, and giving LRU more memory never hurts. **FIFO got worse with more memory** (9 to 10): this is **Belady's anomaly**, and it cannot happen to LRU or OPT because they are *stack algorithms*: the set of pages kept with `n` frames is always a subset of what is kept with `n+1`. A policy without that property can make a bigger cache slower, which is why nobody ships FIFO as a general cache.

```svg
caption: Page faults on 1 2 3 4 1 2 5 1 2 3 4 5. For each policy the blue bar is 3 frames and the lower bar is 4 frames. Only FIFO gets worse when it is given more memory.
<svg viewBox="0 0 760 210" role="img" aria-label="A bar chart of page faults for FIFO, LRU and OPT with three and four frames">
<text class="dim sm" x="90" y="22">page faults (fewer is better)</text>
<text class="big" x="20" y="56">FIFO</text><rect class="blue" x="90" y="40" width="270" height="18" rx="2"/><text class="t-b sm" x="368" y="53">9</text><rect class="bad" x="90" y="62" width="300" height="18" rx="2"/><text class="t-r sm" x="398" y="75">10  more memory, more faults</text><text class="big" x="20" y="108">LRU</text><rect class="blue" x="90" y="92" width="300" height="18" rx="2"/><text class="t-b sm" x="398" y="105">10</text><rect class="live" x="90" y="114" width="240" height="18" rx="2"/><text class="t-g sm" x="338" y="127">8</text><text class="big" x="20" y="160">OPT</text><rect class="blue" x="90" y="144" width="210" height="18" rx="2"/><text class="t-b sm" x="308" y="157">7</text><rect class="live" x="90" y="166" width="180" height="18" rx="2"/><text class="t-g sm" x="278" y="179">6</text>
</svg>
```

## Why LRU, and where it fails

LRU keeps exactly what locality says you will want: the most recently used. Its weakness is the **sequential scan**: a query that reads a table far bigger than the pool touches each page once, and under LRU each of those pages becomes "most recently used" and pushes out the genuinely hot ones. After the scan the pool is full of pages that will never be read again. LRU-K (module 1d) and ARC (module 1e) exist to fix exactly that.

## Why CLOCK

LRU must update a list on **every hit**, and in a multi-threaded buffer pool that update needs a lock on the list, so the hottest path is serialised. CLOCK replaces the list update with setting one bit (cheap, and often lock-free), and does its work only when it must evict. Operating system kernels use CLOCK variants for exactly this reason. The next concept page walks through the sweep.

## What a replacer is, for this course

BusTub's replacers do not own pages. They are told when a frame becomes evictable (`unpin`), when it stops being so (`pin`), and are asked for a `victim`. The buffer pool owns the page table, the dirty bits and the I/O; the replacer owns only the *order*. That narrow interface is why LRU, CLOCK, LRU-K and ARC can all be swapped in behind the same trait.

> [!TIP] Reproduce the table
> Write the reference string and each policy as a small test: a `Vec` of resident pages, a loop over the accesses, a fault counter. If your numbers are not 9/10, 10/8 and 7/6, the policy is wrong. It also makes a good property test for your replacer later: replay a random trace through your LRU and through this naive one and compare victims.
