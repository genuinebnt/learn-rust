//! Port of `src/include/buffer/replacer.h`.

use crate::common::config::FrameId;

/// Tracks which frames may be evicted and picks the victim. BusTub's `Replacer` is an abstract class with a latch inside each
/// implementation; here the methods take `&mut self`, and the buffer pool keeps its replacer inside the mutex that guards its other
/// state, so the replacers themselves need no locking.
pub trait Replacer {
    /// Removes and returns the frame the policy chooses to evict, or `None` if no frame may be evicted.
    fn victim(&mut self) -> Option<FrameId>;

    /// The frame is in use: it must not be evicted until it is unpinned. Pinning a frame the replacer doesn't hold does nothing.
    fn pin(&mut self, frame: FrameId);

    /// The frame is no longer in use: it may now be evicted.
    fn unpin(&mut self, frame: FrameId);

    /// How many frames may be evicted right now.
    fn size(&self) -> usize;
}
