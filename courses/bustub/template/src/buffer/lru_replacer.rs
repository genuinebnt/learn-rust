//! Port of `src/buffer/lru_replacer.cpp`: evict the frame that was unpinned longest ago.

use std::collections::HashMap;

use super::replacer::Replacer;
use crate::common::config::FrameId;
use crate::common::index_list::{Handle, IndexList};

pub struct LruReplacer {
    capacity: usize,
    /// The evictable frames, least recently unpinned first.
    list: IndexList<FrameId>,
    /// Where each evictable frame is in `list`.
    handles: HashMap<FrameId, Handle>,
}

impl LruReplacer {
    pub fn new(num_pages: usize) -> LruReplacer {
        LruReplacer { capacity: num_pages, list: IndexList::new(), handles: HashMap::new() }
    }
}

impl Replacer for LruReplacer {
    fn victim(&mut self) -> Option<FrameId> {
        todo!("1c-03: take the front of the list (the least recently unpinned), forget its handle")
    }

    fn pin(&mut self, frame: FrameId) {
        todo!("1c-03: if the frame is in the replacer, take it out of the list and the map")
    }

    fn unpin(&mut self, frame: FrameId) {
        todo!("1c-03: add the frame at the back unless it is already there (then nothing changes)")
    }

    fn size(&self) -> usize {
        todo!("1c-03: how many frames are in the list")
    }
}
