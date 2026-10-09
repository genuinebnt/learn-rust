//! Locks on half-open key ranges.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Shared,
    Exclusive,
}

#[derive(Debug, PartialEq, Eq)]
pub struct EmptyRange;

#[derive(Default)]
pub struct RangeLocks {
    _rl: (),
}

impl RangeLocks {
    pub fn new() -> RangeLocks {
        todo!("4d-c2: no locks held")
    }

    pub fn try_lock(&mut self, txn: u32, lo: i64, hi: i64, mode: Mode) -> Result<bool, EmptyRange> {
        todo!("4d-c2: refuse on an overlapping incompatible lock of another transaction; otherwise record it")
    }

    pub fn unlock_all(&mut self, txn: u32) -> usize {
        todo!("4d-c2: drop the transaction's locks")
    }

    pub fn held_by(&self, txn: u32) -> usize {
        todo!("4d-c2: how many locks the transaction holds")
    }
}
