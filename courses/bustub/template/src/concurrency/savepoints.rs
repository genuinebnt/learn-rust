//! Savepoints over a map, by undo records.

use std::collections::BTreeMap;

#[derive(Debug, PartialEq, Eq)]
pub struct NoSuchSavepoint;

pub struct SavepointTxn {
    _txn: (),
}

impl SavepointTxn {
    pub fn begin(initial: BTreeMap<i64, i64>) -> SavepointTxn {
        todo!("4b-c5: a transaction over the initial data with nothing to undo")
    }

    pub fn set(&mut self, key: i64, value: i64) {
        todo!("4b-c5: remember what the key was, then write")
    }

    pub fn delete(&mut self, key: i64) {
        todo!("4b-c5: remember what the key was, then remove")
    }

    pub fn get(&self, key: i64) -> Option<i64> {
        todo!("4b-c5: the current value")
    }

    pub fn savepoint(&mut self) -> u64 {
        todo!("4b-c5: mark the current end of the undo log")
    }

    pub fn rollback_to(&mut self, id: u64) -> Result<(), NoSuchSavepoint> {
        todo!("4b-c5: undo back to the mark, newest first; drop the later savepoints")
    }

    pub fn release(&mut self, id: u64) -> Result<(), NoSuchSavepoint> {
        todo!("4b-c5: forget the savepoint and every later one, keeping their changes")
    }

    pub fn rollback_all(&mut self) {
        todo!("4b-c5: undo everything")
    }

    pub fn commit(self) -> BTreeMap<i64, i64> {
        todo!("4b-c5: the final map")
    }
}
