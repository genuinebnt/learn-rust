//! A tiny simulator for replacement policies: replay a trace of page accesses through a pool of fixed size and count the hits.

use std::collections::HashMap;

use crate::buffer::replacer::FrameReplacer;
use crate::common::config::{FrameId, PageId};

/// Replays `trace` (page numbers, in the order they are used) through a pool of `capacity` frames, with `replacer` choosing the victim, and
/// returns how many accesses found their page already in the pool. A miss with a free frame uses it; a miss with the pool full evicts the
/// replacer's victim and reuses its frame. The replacer sees every access (`record_access(frame, page)`), and every page is evictable as soon as
/// it is used (nothing stays pinned). A capacity of 0 has no hits.
pub fn simulate(trace: &[u32], capacity: usize, mut replacer: Box<dyn FrameReplacer>) -> usize {
    // @begin 1d-c1
    let mut table: HashMap<u32, FrameId> = HashMap::new();
    let mut page_of: HashMap<FrameId, u32> = HashMap::new();
    let mut next_free = 0;
    let mut hits = 0;
    if capacity == 0 {
        return 0;
    }
    for &page in trace {
        let frame = match table.get(&page) {
            Some(&f) => {
                hits += 1;
                f
            }
            None => {
                let f = if next_free < capacity {
                    next_free += 1;
                    FrameId(next_free - 1)
                } else {
                    let victim = replacer.evict().expect("every frame is evictable, so there is a victim");
                    let old = page_of.remove(&victim).unwrap();
                    table.remove(&old);
                    victim
                };
                table.insert(page, f);
                page_of.insert(f, page);
                f
            }
        };
        replacer.record_access(frame, PageId(page as i32));
        replacer.set_evictable(frame, true);
    }
    hits
    //~ todo!("1d-c1: replay the trace through a pool of frames, counting the hits")
    // @end
}

/// The best any policy can do: Belady's rule evicts the page whose next use is **furthest in the future** (or never). It needs the whole trace
/// in advance, so no real system can use it, but it is the yardstick every real policy is measured against: no policy can have more hits.
pub fn belady_hits(trace: &[u32], capacity: usize) -> usize {
    // @begin 1d-c1
    if capacity == 0 {
        return 0;
    }
    let mut pool: Vec<u32> = Vec::new();
    let mut hits = 0;
    for (i, &page) in trace.iter().enumerate() {
        if pool.contains(&page) {
            hits += 1;
            continue;
        }
        if pool.len() == capacity {
            let next_use = |p: u32| trace[i + 1..].iter().position(|&x| x == p).unwrap_or(usize::MAX);
            let (victim, _) = pool.iter().enumerate().max_by_key(|&(_, &p)| next_use(p)).unwrap();
            pool.swap_remove(victim);
        }
        pool.push(page);
    }
    hits
    //~ todo!("1d-c1: the optimal number of hits for this trace and pool size")
    // @end
}
