//! Port of `src/buffer/clock_replacer.cpp`: the CLOCK policy, an approximation of LRU that needs one bit per frame.
//!
//! The frames sit on a ring with a "hand". Each has a reference bit, set when the frame is unpinned. To find a victim the hand
//! sweeps: a frame with its bit set gets a second chance (the bit is cleared, the hand moves on); the first frame with the bit
//! clear is the victim.

use super::replacer::Replacer;
use crate::common::config::FrameId;

pub struct ClockReplacer {
    capacity: usize,
    /// The evictable frames in ring order, each with its reference bit.
    ring: Vec<(FrameId, bool)>,
    /// Index into `ring` of the frame the hand points at.
    hand: usize,
}

impl ClockReplacer {
    pub fn new(num_pages: usize) -> ClockReplacer {
        ClockReplacer { capacity: num_pages, ring: Vec::new(), hand: 0 }
    }
}

impl Replacer for ClockReplacer {
    fn unpin(&mut self, frame: FrameId) {
        todo!("1c-08: a frame already on the ring gets its reference bit set; a new one is added at the end of the ring with its bit set")
    }

    fn size(&self) -> usize {
        todo!("1c-08: how many frames are on the ring")
    }

    fn pin(&mut self, frame: FrameId) {
        todo!("1c-10: take the frame off the ring; the hand must keep pointing at the same frame it did (wrapping to 0 past the end)")
    }

    fn victim(&mut self) -> Option<FrameId> {
        todo!("1c-09: sweep the hand: clear set bits and move on, evict the first frame whose bit is clear")
    }
}
