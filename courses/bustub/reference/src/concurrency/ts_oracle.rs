//! A timestamp oracle: commit timestamps and read timestamps.

use std::collections::BTreeSet;

#[derive(Default)]
pub struct TsOracle {
    reserved: u64,
    finished: BTreeSet<u64>,
}

impl TsOracle {
    pub fn new() -> TsOracle {
        TsOracle::default()
    }

    /// The next commit timestamp.
    pub fn reserve(&mut self) -> u64 {
        self.reserved += 1;
        self.reserved
    }

    /// The commit with timestamp `ts` has put all its writes in place.
    pub fn finish(&mut self, ts: u64) {
        if ts >= 1 && ts <= self.reserved {
            self.finished.insert(ts);
        }
    }

    /// The read timestamp for a new transaction.
    pub fn begin(&self) -> u64 {
        // @begin 4a-c3
        let mut t = 0;
        while t < self.reserved && self.finished.contains(&(t + 1)) {
            t += 1;
        }
        t
        //~ self.finished.iter().next_back().copied().unwrap_or(0)
        // @end
    }
}
