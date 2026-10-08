//! Port of `src/buffer/lru_k_replacer.cpp`: the LRU-K policy (O'Neil, O'Neil, Weikum, SIGMOD 1993).
//!
//! LRU-K evicts the frame whose **backward k-distance** is largest: the time since its k-th most recent access. A frame with fewer
//! than k recorded accesses has an infinite distance, and among those the one whose *first* access is oldest goes first (plain LRU).
//! One long scan can't flush the pool, because scanned pages have been touched once and are evicted before pages touched twice.

use std::collections::{HashMap, VecDeque};

use crate::common::config::FrameId;

/// What the replacer remembers about one frame.
pub struct LruKNode {
    /// The timestamps of the last (up to k) accesses, oldest first.
    history: VecDeque<usize>,
    k: usize,
    fid: FrameId,
    is_evictable: bool,
}

impl LruKNode {
    pub fn new(fid: FrameId, k: usize) -> LruKNode {
        LruKNode { history: VecDeque::new(), k, fid, is_evictable: false }
    }

    /// Notes an access at time `timestamp`. Only the `k` most recent accesses are kept.
    pub fn record(&mut self, timestamp: usize) {
        todo!("1d-01: add the timestamp at the back; if there are now more than k, drop the oldest")
    }

    /// The timestamp of the k-th most recent access, or `None` if there have been fewer than k accesses (distance +infinity).
    pub fn kth_timestamp(&self) -> Option<usize> {
        todo!("1d-01: the oldest timestamp kept, but only once k accesses have been recorded")
    }

    /// The oldest timestamp kept.
    pub fn first_timestamp(&self) -> Option<usize> {
        self.history.front().copied()
    }

    pub fn frame_id(&self) -> FrameId {
        self.fid
    }

    pub fn is_evictable(&self) -> bool {
        self.is_evictable
    }
}


pub struct LruKReplacer {
    node_store: HashMap<FrameId, LruKNode>,
    /// Advances by one on every recorded access.
    current_timestamp: usize,
    /// How many frames are evictable.
    curr_size: usize,
    replacer_size: usize,
    k: usize,
}

impl LruKReplacer {
    /// A replacer for frames `0..num_frames` with history length `k` (at least 1).
    pub fn new(num_frames: usize, k: usize) -> LruKReplacer {
        todo!("1d-01: the maps and counters start empty; k must be at least 1")
    }

    /// Records an access to `frame` at the current time. A frame seen for the first time starts out not evictable.
    /// Panics if `frame` is not in `0..num_frames`.
    pub fn record_access(&mut self, frame: FrameId) {
        todo!("1d-01: panic for a frame id out of range; create the node if it is new; record the access at the current time and advance the clock")
    }

    /// Marks `frame` evictable or not. Unknown frames are ignored.
    pub fn set_evictable(&mut self, frame: FrameId, evictable: bool) {
        todo!("1d-02: ignore unknown frames; change the flag and keep the count of evictable frames right")
    }

    /// How many frames are evictable.
    pub fn size(&self) -> usize {
        todo!("1d-01: the number of evictable frames")
    }

    /// The best victim among the evictable frames by a scan of all of them (O(n)).
    fn pick_victim(&self) -> Option<FrameId> {
        todo!("1d-02: among the evictable frames, the one whose backward k-distance is largest")
    }

    /// Evicts the frame with the largest backward k-distance among the evictable frames, forgetting its history.
    /// `None` if no frame is evictable.
    pub fn evict(&mut self) -> Option<FrameId> {
        todo!("1d-02: pick the victim, drop its node, keep the count right, return it")
    }

    /// Forgets `frame`'s node (and its place in the eviction order).
    fn remove_node(&mut self, frame: FrameId) {
        todo!("1d-02: drop the node; if it was evictable the count of evictable frames goes down")
    }

    /// Removes an evictable frame and its history, whatever its distance. Unknown frames are ignored.
    /// Panics if the frame is not evictable.
    pub fn remove(&mut self, frame: FrameId) {
        todo!("1d-03: ignore unknown frames; panic for a frame that is not evictable; otherwise drop it")
    }
}
