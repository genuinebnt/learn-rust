//! Port of `src/buffer/lru_replacer.cpp`: evict the frame that was unpinned longest ago.
//!
//! The policy, in the terms the buffer pool sees: the replacer holds the frames that may be evicted ("unpinned" frames). Unpinning a
//! frame that is not there adds it as the **most recently used**; unpinning one that is already there changes nothing (it does not
//! become more recent). Pinning a frame removes it. `victim` removes and returns the **least recently used** frame.

use super::replacer::Replacer;
use crate::common::config::FrameId;

// TODO(1c-02): your imports go here.

pub struct LruReplacer {
    // TODO(1c-02): the fields are yours. `IndexList` from 1c-01 is one way to get O(1) removal from the middle; a design of your own is just as good.
}

impl LruReplacer {
    /// A replacer for a pool of `num_pages` frames. Unpinning more distinct frames than that is a bug in the caller: it panics.
    pub fn new(num_pages: usize) -> LruReplacer {
        todo!("1c-02: an empty replacer for `num_pages` frames")
    }
}

impl Replacer for LruReplacer {
    fn victim(&mut self) -> Option<FrameId> {
        todo!("1c-02: remove and return the least recently used frame, if there is one")
    }

    fn pin(&mut self, frame: FrameId) {
        todo!("1c-02: the frame may not be evicted any more; if it was not in the replacer, nothing happens")
    }

    fn unpin(&mut self, frame: FrameId) {
        todo!("1c-02: the frame may be evicted; if it is new it is the most recently used, if it was already there nothing changes")
    }

    fn size(&self) -> usize {
        todo!("1c-02: how many frames may be evicted")
    }
}
