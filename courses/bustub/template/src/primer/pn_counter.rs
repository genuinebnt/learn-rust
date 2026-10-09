//! A positive-negative counter CRDT.

use std::collections::BTreeMap;

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct PnCounter {
    _pn: (),
}

impl PnCounter {
    pub fn new() -> PnCounter {
        todo!("0d-c4: a counter nobody has changed")
    }

    pub fn inc(&mut self, node: u32, n: u64) {
        todo!("0d-c4: this node added n")
    }

    pub fn dec(&mut self, node: u32, n: u64) {
        todo!("0d-c4: this node took n away")
    }

    pub fn value(&self) -> i64 {
        todo!("0d-c4: all added minus all removed")
    }

    pub fn merge(&mut self, other: &PnCounter) {
        todo!("0d-c4: for each node the larger count, separately for added and removed")
    }
}
