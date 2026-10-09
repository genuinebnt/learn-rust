//! A tiny simulator for replacement policies: replay a trace of page accesses through a pool of fixed size and count the hits.

use std::collections::HashMap;

use crate::buffer::replacer::FrameReplacer;
use crate::common::config::{FrameId, PageId};

/// Replays `trace` (page numbers, in the order they are used) through a pool of `capacity` frames, with `replacer` choosing the victim, and
/// returns how many accesses found their page already in the pool. A miss with a free frame uses it; a miss with the pool full evicts the
/// replacer's victim and reuses its frame. The replacer sees every access (`record_access(frame, page)`), and every page is evictable as soon as
/// it is used (nothing stays pinned). A capacity of 0 has no hits.
pub fn simulate(trace: &[u32], capacity: usize, mut replacer: Box<dyn FrameReplacer>) -> usize {
    todo!("1d-c1: replay the trace through a pool of frames, counting the hits")
}

/// The best any policy can do: Belady's rule evicts the page whose next use is **furthest in the future** (or never). It needs the whole trace
/// in advance, so no real system can use it, but it is the yardstick every real policy is measured against: no policy can have more hits.
pub fn belady_hits(trace: &[u32], capacity: usize) -> usize {
    todo!("1d-c1: the optimal number of hits for this trace and pool size")
}
