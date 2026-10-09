//! Port of `src/buffer/clock_replacer.cpp`: the CLOCK policy, an approximation of LRU that needs one bit per frame.
//!
//! The evictable frames sit on a **ring** with a **hand** pointing at one of them. Each frame has a reference bit, set when the
//! frame is unpinned.
//!
//! - `unpin(f)`: if `f` is on the ring, its bit is set (it keeps its place). Otherwise it joins the ring just **behind the hand**
//!   (the last place the hand will reach) with its bit set.
//! - `pin(f)`: `f` leaves the ring. The hand keeps pointing at the same frame; if `f` was the one under the hand, it moves on to
//!   the next.
//! - `victim()`: the hand sweeps. A frame with its bit set gets a second chance: the bit is cleared and the hand moves on. The first
//!   frame found with its bit clear is removed and returned; the hand then points at the frame after it.

use super::replacer::Replacer;
use crate::common::config::FrameId;

pub struct ClockReplacer {
    // TODO(1c-03): the fields are yours: a ring, a hand, and a reference bit per frame.
}

impl ClockReplacer {
    /// A replacer for a pool of `num_pages` frames. Unpinning more distinct frames than that is a bug in the caller: it panics.
    pub fn new(num_pages: usize) -> ClockReplacer {
        todo!("1c-03: an empty replacer for `num_pages` frames")
    }
}

impl Replacer for ClockReplacer {
    fn unpin(&mut self, frame: FrameId) {
        todo!("1c-03: a frame already on the ring gets its reference bit set; a new one joins just behind the hand, bit set")
    }

    fn size(&self) -> usize {
        todo!("1c-03: how many frames are on the ring")
    }

    fn pin(&mut self, frame: FrameId) {
        todo!("1c-03: take the frame off the ring; the hand keeps pointing at the same frame it did (wrapping past the end)")
    }

    fn victim(&mut self) -> Option<FrameId> {
        todo!("1c-03: sweep the hand: clear set bits and move on, remove and return the first frame whose bit is clear")
    }
}
