//! Batching commit acknowledgements behind one log flush.

use std::collections::VecDeque;

pub struct GroupCommit {
    _gc: (),
}

impl GroupCommit {
    pub fn new(max_batch: usize, max_wait: u64) -> GroupCommit {
        todo!("4c-c2: an empty queue with the two limits")
    }

    pub fn submit(&mut self, lsn: u64, now: u64) {
        todo!("4c-c2: queue the commit with the time it arrived")
    }

    pub fn poll(&mut self, now: u64) -> Option<Vec<u64>> {
        todo!("4c-c2: a batch when the queue is full enough or the oldest has waited long enough")
    }

    pub fn flush_all(&mut self) -> Vec<u64> {
        todo!("4c-c2: everything that waits")
    }

    pub fn pending(&self) -> usize {
        todo!("4c-c2: how many commits wait")
    }
}
