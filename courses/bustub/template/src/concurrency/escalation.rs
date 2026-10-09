//! Lock escalation: many row locks become one table lock.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, PartialEq, Eq)]
pub enum RowLockResult {
    Granted,
    Covered,
    Escalate { table: u32, released: Vec<u64> },
}

pub struct Escalator {
    _esc: (),
}

impl Escalator {
    pub fn new(threshold: usize) -> Escalator {
        todo!("4d-c5: nothing locked")
    }

    pub fn row_lock(&mut self, txn: u32, table: u32, row: u64) -> RowLockResult {
        todo!("4d-c5: count the transaction's row locks on the table; past the threshold replace them by a table lock")
    }

    pub fn holds_table(&self, txn: u32, table: u32) -> bool {
        todo!("4d-c5: does the transaction hold the table lock")
    }

    pub fn row_count(&self, txn: u32, table: u32) -> usize {
        todo!("4d-c5: how many row locks")
    }

    pub fn release_all(&mut self, txn: u32) {
        todo!("4d-c5: forget every lock of the transaction")
    }
}
