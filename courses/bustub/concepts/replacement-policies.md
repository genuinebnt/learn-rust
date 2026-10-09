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

## In real code

### Using it: simulate the policies and reproduce the numbers

Policies are easiest to understand by replaying a trace. This simulator counts faults for FIFO, LRU and the unreachable ideal, OPT, on the reference string from the figure, and is the harness you can reuse to check your own replacers against a model.

```rust test
fn faults(trace: &[u32], frames: usize, mut choose_victim: impl FnMut(&[u32], usize, &[u32]) -> usize, on_hit: impl Fn(&mut Vec<u32>, usize)) -> usize {
    let mut resident: Vec<u32> = Vec::new();                       // order = the policy's order (oldest first)
    let mut faults = 0;
    for (t, &page) in trace.iter().enumerate() {
        if let Some(pos) = resident.iter().position(|&p| p == page) {
            on_hit(&mut resident, pos);                            // a hit: LRU refreshes, FIFO ignores
            continue;
        }
        faults += 1;
        if resident.len() == frames {
            let v = choose_victim(&resident, t, trace);
            resident.remove(v);
        }
        resident.push(page);
    }
    faults
}

fn fifo(trace: &[u32], n: usize) -> usize { faults(trace, n, |_, _, _| 0, |_, _| {}) }
fn lru(trace: &[u32], n: usize) -> usize {
    faults(trace, n, |_, _, _| 0, |r, pos| { let p = r.remove(pos); r.push(p); })                // move the hit page to the newest end
}
fn opt(trace: &[u32], n: usize) -> usize {
    faults(trace, n, |resident, t, trace| {
        // evict the page whose NEXT use is farthest away (or never)
        (0..resident.len()).max_by_key(|&i| trace[t + 1..].iter().position(|&p| p == resident[i]).unwrap_or(usize::MAX)).unwrap()
    }, |_, _| {})
}

#[test]
fn the_reference_string() {
    let trace = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5];
    assert_eq!((fifo(&trace, 3), fifo(&trace, 4)), (9, 10));         // Belady's anomaly: more memory, MORE faults
    assert_eq!((lru(&trace, 3), lru(&trace, 4)), (10, 8));
    assert_eq!((opt(&trace, 3), opt(&trace, 4)), (7, 6));            // the unreachable lower bound
}

#[test]
fn lru_never_gets_worse_with_more_memory() {
    // LRU and OPT are stack algorithms: the set kept with n frames is a subset of the set kept with n+1.
    let mut x = 1u32;
    let trace: Vec<u32> = (0..300).map(|_| { x = x.wrapping_mul(1103515245).wrapping_add(12345); (x >> 16) % 12 }).collect();
    for n in 1..11 {
        assert!(lru(&trace, n + 1) <= lru(&trace, n), "n = {n}");
    }
}
```

```rust test
#[test]
fn a_scan_flushes_lru_but_not_a_frequency_aware_policy() {
    // A hot set {0, 1, 2} is used again and again; then one long scan touches 50 pages once each.
    let hot = [0u32, 1, 2];
    let mut lru: Vec<u32> = vec![];
    let frames = 4;
    let touch = |lru: &mut Vec<u32>, p: u32| {
        if let Some(i) = lru.iter().position(|&x| x == p) { lru.remove(i); } else if lru.len() == frames { lru.remove(0); }
        lru.push(p);
    };
    for _ in 0..10 { for &p in &hot { touch(&mut lru, p); } }
    for p in 100..150 { touch(&mut lru, p); }                         // the scan
    assert!(hot.iter().all(|h| !lru.contains(h)), "LRU lost the hot set: {lru:?}");   // the scan evicted everything useful
}
```

### In the exercises

- **1c-02 and 1c-03:** LRU and CLOCK behind the one `Replacer` trait. The simulator above is a way to compare policies on a trace; the boss stage replays a trace through both to show when they agree.
- **1d and 1e:** LRU-K and ARC exist because of the last test: a scan defeats plain LRU.
- **1f-02:** the buffer pool calls the replacer on every access and every miss; the hit ratio you measure there is the `faults` count above, over the number of accesses.

### Where it is used

- **Operating systems**: Linux's page cache uses a two-list "active/inactive" approximation of LRU (a CLOCK-like second chance), because exact LRU is too expensive on every access.
- **Database buffer pools**: InnoDB's LRU has a midpoint so a scan enters at the old end; PostgreSQL uses a clock sweep (usage counts) over its buffers.
- **CPU caches and TLBs** use pseudo-LRU in hardware; **CDNs and Redis** use approximate LRU/LFU (`maxmemory-policy`).
- **Memoisation and `lru` caches** in application code: the `lru` crate's `LruCache` is this policy in a few lines of API.
