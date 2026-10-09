//! Which dirty pages are due for a background flush.

use std::collections::BTreeMap;

pub struct WriteBehind {
    _wb: (),
}

impl WriteBehind {
    pub fn new() -> WriteBehind {
        todo!("1f-c3: nothing is dirty")
    }

    pub fn mark_dirty(&mut self, page: u32, now: u64) {
        todo!("1f-c3: remember when the page first became dirty")
    }

    /// Pages dirty for at least `max_age` as of `now`, oldest first (ties by page number).
    pub fn due(&self, now: u64, max_age: u64) -> Vec<u32> {
        todo!("1f-c3: the pages that have been dirty long enough, oldest first")
    }

    pub fn flushed(&mut self, page: u32) -> bool {
        todo!("1f-c3: forget the page")
    }

    pub fn dirty_count(&self) -> usize {
        todo!("1f-c3: how many pages are dirty")
    }

    /// The page that has been dirty longest, with the time it became dirty.
    pub fn oldest(&self) -> Option<(u32, u64)> {
        todo!("1f-c3: the oldest dirty page")
    }
}

impl Default for WriteBehind {
    fn default() -> Self {
        WriteBehind::new()
    }
}
