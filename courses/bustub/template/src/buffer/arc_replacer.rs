//! Port of `src/buffer/arc_replacer.cpp`: the ARC replacement policy (Megiddo and Modha, FAST 2003).
//!
//! ARC keeps four lists. `mru` holds live frames seen **once** recently, `mfu` holds live frames seen **at least twice**. The two
//! **ghost** lists remember the page ids (not the data) of pages recently evicted from `mru` and `mfu`. A hit on a ghost tells ARC
//! which side it evicted too eagerly, and it shifts the target size of `mru` (`p`) towards that side. So ARC adapts between
//! recency-heavy and frequency-heavy workloads, and a scan can't flush the frequently used pages.
//!
//! Every list is an [`IndexList`] with the **oldest at the front and the newest at the back**, so eviction takes from the front.

use std::collections::HashMap;

use crate::common::config::{FrameId, PageId};
use crate::common::index_list::{Handle, IndexList};

/// Which of the four lists an entry is on.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ArcStatus {
    Mru,
    Mfu,
    MruGhost,
    MfuGhost,
}

/// A frame that holds a page right now (on `mru` or `mfu`).
struct Alive {
    page_id: PageId,
    evictable: bool,
    status: ArcStatus,
    handle: Handle,
}

/// A page that was evicted recently (on `mru_ghost` or `mfu_ghost`). It has no frame.
struct Ghost {
    status: ArcStatus,
    handle: Handle,
}

pub struct ArcReplacer {
    mru: IndexList<FrameId>,
    mfu: IndexList<FrameId>,
    mru_ghost: IndexList<PageId>,
    mfu_ghost: IndexList<PageId>,
    /// Where each live frame is.
    alive: HashMap<FrameId, Alive>,
    /// Where each ghost page is.
    ghost: HashMap<PageId, Ghost>,
    /// How many live frames are evictable.
    curr_size: usize,
    /// `p` in the paper: how many frames `mru` should hold.
    mru_target_size: usize,
    /// `c` in the paper: the number of frames.
    replacer_size: usize,
}

impl ArcReplacer {
    pub fn new(num_frames: usize) -> ArcReplacer {
        todo!("1e-01: four empty lists, two empty maps, the counters at zero; the replacer's size is the number of frames")
    }

    /// How many live frames are evictable.
    pub fn size(&self) -> usize {
        todo!("1e-01: the number of evictable frames")
    }



    /// `frame` now holds (or is accessed as) `page_id`.
    pub fn record_access(&mut self, frame: FrameId, page_id: PageId) {
        todo!("1e-01: a new frame goes to the newest end of mru and is not evictable until marked")
    }

    /// Marks a live frame evictable or not. Unknown frames are ignored.
    pub fn set_evictable(&mut self, frame: FrameId, evictable: bool) {
        todo!("1e-01: ignore unknown frames; change the flag and keep the count right")
    }

    /// The oldest evictable frame on `mru` or `mfu`.
    fn oldest_evictable(&self, status: ArcStatus) -> Option<FrameId> {
        todo!("1e-02: walk the list from the oldest end for the first evictable frame")
    }

    /// Evicts a frame: from `mru` if it holds at least `p` frames, else from `mfu` (and from the other list if the first has no
    /// evictable frame). The victim's page becomes a ghost. `None` if no frame is evictable.
    pub fn evict(&mut self) -> Option<FrameId> {
        todo!("1e-02: take the oldest evictable frame, forget its frame, remember its page as a ghost of the same side")
    }

    /// Removes an evictable frame without leaving a ghost (the page was deleted, not evicted). Unknown frames are ignored.
    /// Panics if the frame is not evictable.
    pub fn remove(&mut self, frame: FrameId) {
        todo!("1e-03: ignore unknown frames; panic for a frame that is not evictable; drop it from its list and the map; no ghost")
    }
}
