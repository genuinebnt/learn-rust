//! Port of `src/include/buffer/replacer.h`.

use crate::common::config::{FrameId, PageId};

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

/// What a buffer pool needs from a replacement policy. `ArcReplacer` (module 1e) and `LruKReplacer` (module 1d) both implement it, and
/// so can any policy of your own: the pool never names a concrete replacer, so any correct one fits under it.
///
/// A **frame** holds a **page**; the replacer decides which evictable frame to give up. The contract, which every implementation keeps:
///
/// - `record_access(frame, page)` notes that `frame` now holds `page`, or that the page it holds was used again. A frame that is
///   new to the replacer starts out **not evictable**.
/// - `set_evictable(frame, evictable)` says whether the frame may be evicted. Frames the replacer does not know are ignored.
/// - `evict()` removes and returns an evictable frame, or `None` if none is evictable. The replacer forgets the frame.
/// - `remove(frame)` forgets an evictable frame (its page was deleted). It panics if the frame is known but not evictable.
/// - `size()` is the number of evictable frames.
pub trait FrameReplacer: Send {
    fn record_access(&mut self, frame: FrameId, page: PageId);
    fn set_evictable(&mut self, frame: FrameId, evictable: bool);
    fn evict(&mut self) -> Option<FrameId>;
    fn remove(&mut self, frame: FrameId);
    fn size(&self) -> usize;
}
