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

## In real code

### Using it: the four lists as runnable code

A compact model of the rules above. Lists are `VecDeque`s with linear lookups so the logic is readable; the stages ask for O(1) with maps from page to position, which is a data-structure change, not a rule change. The driver evicts before admitting a page when the cache is full, and the test replays the traces you can check by hand.

```rust test
use std::collections::VecDeque;

type Page = u32;

struct Arc { c: usize, p: usize, mru: VecDeque<Page>, mfu: VecDeque<Page>, mru_ghost: VecDeque<Page>, mfu_ghost: VecDeque<Page> }

fn take(list: &mut VecDeque<Page>, page: Page) -> bool {
    match list.iter().position(|&x| x == page) { Some(i) => { list.remove(i); true } None => false }
}

impl Arc {
    fn new(c: usize) -> Self { Arc { c, p: 0, mru: Default::default(), mfu: Default::default(), mru_ghost: Default::default(), mfu_ghost: Default::default() } }
    fn live(&self) -> usize { self.mru.len() + self.mfu.len() }

    fn evict(&mut self) {
        let from_mru = !self.mru.is_empty() && (self.mru.len() >= self.p || self.mfu.is_empty());
        if from_mru { let v = self.mru.pop_front().unwrap(); self.mru_ghost.push_back(v); }
        else        { let v = self.mfu.pop_front().unwrap(); self.mfu_ghost.push_back(v); }
    }

    fn access(&mut self, page: Page) {
        if self.mru.contains(&page) || self.mfu.contains(&page) {          // rule 1: a hit
            take(&mut self.mru, page); take(&mut self.mfu, page);
            self.mfu.push_back(page);
            return;
        }
        if self.live() == self.c { self.evict(); }                         // make room in the live lists first
        if self.mru_ghost.contains(&page) {                                // rule 2: recency was undervalued
            let step = if self.mfu_ghost.len() > self.mru_ghost.len() { self.mfu_ghost.len() / self.mru_ghost.len() } else { 1 };
            self.p = (self.p + step).min(self.c);
            take(&mut self.mru_ghost, page);
            self.mfu.push_back(page);
        } else if self.mfu_ghost.contains(&page) {                         // rule 3: frequency was undervalued
            let step = if self.mru_ghost.len() > self.mfu_ghost.len() { self.mru_ghost.len() / self.mfu_ghost.len() } else { 1 };
            self.p = self.p.saturating_sub(step);
            take(&mut self.mfu_ghost, page);
            self.mfu.push_back(page);
        } else {                                                           // rule 4: a new page; bound the ghosts first
            if self.mru.len() + self.mru_ghost.len() >= self.c { self.mru_ghost.pop_front(); }
            else if self.mru.len() + self.mfu.len() + self.mru_ghost.len() + self.mfu_ghost.len() >= 2 * self.c { self.mfu_ghost.pop_front(); }
            self.mru.push_back(page);
        }
    }

    fn check(&self) {
        assert!(self.live() <= self.c);
        assert!(self.mru.len() + self.mru_ghost.len() <= self.c);
        assert!(self.live() + self.mru_ghost.len() + self.mfu_ghost.len() <= 2 * self.c);
        assert!(self.p <= self.c);
        let mut all: Vec<_> = self.mru.iter().chain(&self.mfu).chain(&self.mru_ghost).chain(&self.mfu_ghost).collect();
        let n = all.len();
        all.sort(); all.dedup();
        assert_eq!(all.len(), n, "a page is in two lists at once");
    }
}

#[test]
fn ghost_hits_move_the_target() {
    let v = |l: &VecDeque<Page>| l.iter().copied().collect::<Vec<_>>();
    let mut a = Arc::new(3);
    a.access(9); a.access(9);                                  // 9 is seen twice: it lives in mfu
    for page in [1, 2, 3] { a.access(page); }                  // 3 evicts 1 from mru; 1 becomes a ghost
    assert_eq!((v(&a.mru), v(&a.mru_ghost), v(&a.mfu)), (vec![2, 3], vec![1], vec![9]));
    a.access(1);                                               // ghost hit in mru_ghost: p goes 0 -> 1, page 1 re-enters in mfu
    assert_eq!((a.p, v(&a.mfu)), (1, vec![9, 1]));
    a.access(2);                                               // another one: p goes to 2
    assert_eq!(a.p, 2);
    a.check();
    a.access(4);                                               // new page; mru is smaller than p, so the victim comes from mfu
    assert_eq!(v(&a.mfu_ghost), vec![9]);
    a.access(9);                                               // ghost hit in mfu_ghost: frequency was undervalued, p goes DOWN
    assert_eq!(a.p, 1);
    a.check();
}

#[test]
fn a_scan_does_not_flush_the_frequent_pages() {
    let mut a = Arc::new(4);
    for _ in 0..2 { for hot in [1, 2] { a.access(hot); } }     // 1 and 2 reach mfu
    for scan in 100..140 { a.access(scan); a.check(); }
    assert!(a.mfu.contains(&1) && a.mfu.contains(&2), "the scan evicted the frequent pages");
}

#[test]
fn the_bounds_hold_on_a_random_workload() {
    let mut a = Arc::new(8);
    let mut x = 12345u64;
    for _ in 0..5000 {
        x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        let page = if (x >> 60) < 6 { ((x >> 33) % 6) as u32 } else { ((x >> 33) % 40) as u32 };   // skewed: a hot set and a long tail
        a.access(page);
        a.check();
    }
}
```

### In the exercises

- **1e-01 to 1e-03:** the same algorithm in three steps: the contract and live frames; the `mru`/`mfu` split with hits and eviction; ghost hits, the adaptive target `p` and the bounds on the four lists. The first test above is the target moving; the `check` function is the bounds.
- **1f-02:** the buffer pool can use `ArcReplacer`; a scan workload is where the hit ratio differs from LRU.

### Where it is used

- **ZFS** uses ARC as its main read cache (the Linux ZFS module reports it as the "ARC size" in `arc_summary`); some storage controllers (IBM's) use it for the same reason.
- **PostgreSQL 8.0** shipped an ARC buffer manager and replaced it within a release because of the patent; the clock-sweep it has today descends from that decision.
- **The ghost-list idea** (remember what you evicted, and treat a re-request as feedback) appears in CAR, CLOCK-Pro, and in many modern caches' admission policies.
