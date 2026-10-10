//! Lock escalation: many row locks become one table lock.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, PartialEq, Eq)]
pub enum RowLockResult {
    Granted,
    Covered,
    Escalate { table: u32, released: Vec<u64> },
}

pub struct Escalator {
    // @begin 4d-c5
    threshold: usize,
    rows: BTreeMap<(u32, u32), BTreeSet<u64>>,
    tables: BTreeSet<(u32, u32)>,
    //~ _esc: (),
    // @end
}

impl Escalator {
    pub fn new(threshold: usize) -> Escalator {
        // @begin 4d-c5
        Escalator { threshold, rows: BTreeMap::new(), tables: BTreeSet::new() }
        //~ todo!("4d-c5: nothing locked")
        // @end
    }

    pub fn row_lock(&mut self, txn: u32, table: u32, row: u64) -> RowLockResult {
        // @begin 4d-c5
        if self.tables.contains(&(txn, table)) {
            return RowLockResult::Covered;
        }
        let set = self.rows.entry((txn, table)).or_default();
        if set.contains(&row) {
            return RowLockResult::Granted;
        }
        if set.len() + 1 > self.threshold {
            let released: Vec<u64> = std::mem::take(set).into_iter().collect();
            self.rows.remove(&(txn, table));
            self.tables.insert((txn, table));
            return RowLockResult::Escalate { table, released };
        }
        set.insert(row);
        RowLockResult::Granted
        //~ todo!("4d-c5: count the transaction's row locks on the table; past the threshold replace them by a table lock")
        // @end
    }

    pub fn holds_table(&self, txn: u32, table: u32) -> bool {
        // @begin 4d-c5
        self.tables.contains(&(txn, table))
        //~ todo!("4d-c5: does the transaction hold the table lock")
        // @end
    }

    pub fn row_count(&self, txn: u32, table: u32) -> usize {
        // @begin 4d-c5
        self.rows.get(&(txn, table)).map_or(0, BTreeSet::len)
        //~ todo!("4d-c5: how many row locks")
        // @end
    }

    pub fn release_all(&mut self, txn: u32) {
        // @begin 4d-c5
        self.rows.retain(|&(t, _), _| t != txn);
        self.tables.retain(|&(t, _)| t != txn);
        //~ todo!("4d-c5: forget every lock of the transaction")
        // @end
    }
}
