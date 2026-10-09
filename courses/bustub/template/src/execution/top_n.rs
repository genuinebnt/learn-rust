//! ORDER BY ... LIMIT n with memory for n rows.

use std::collections::BinaryHeap;

pub struct TopN {
    _topn: (),
}

impl TopN {
    pub fn new(n: usize) -> TopN {
        todo!("3g-c2: an empty selector for `n` rows")
    }

    pub fn push(&mut self, key: i64, payload: u32) {
        todo!("3g-c2: keep the `n` best seen so far")
    }

    pub fn len(&self) -> usize {
        todo!("3g-c2: rows held")
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn finish(self) -> Vec<(i64, u32)> {
        todo!("3g-c2: the held rows in key order, earlier arrivals first among equals")
    }
}
