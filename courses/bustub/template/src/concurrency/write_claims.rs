//! Claims on keys for first-updater-wins conflict detection.

use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq)]
pub struct Conflict {
    pub owner: u64,
}

#[derive(Default)]
pub struct WriteClaims {
    _claims: (),
}

impl WriteClaims {
    pub fn new() -> WriteClaims {
        todo!("4b-c1: nothing is claimed")
    }

    pub fn claim(&mut self, txn: u64, key: i64) -> Result<(), Conflict> {
        todo!("4b-c1: take the key if it is free or already yours")
    }

    pub fn release_all(&mut self, txn: u64) -> usize {
        todo!("4b-c1: free every key the transaction holds")
    }

    pub fn owner_of(&self, key: i64) -> Option<u64> {
        todo!("4b-c1: who holds the key")
    }
}
