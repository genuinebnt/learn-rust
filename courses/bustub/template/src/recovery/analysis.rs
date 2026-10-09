//! The analysis pass of recovery.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LogRec {
    Begin(u32),
    Update(u32, u32),
    Commit(u32),
    Abort(u32),
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Analysis {
    pub active: BTreeSet<u32>,
    /// page -> the LSN of the first record that dirtied it
    pub dirty: BTreeMap<u32, u64>,
}

/// `checkpoint` is the state recorded by the last checkpoint; `after` are `(lsn, record)` pairs in log order.
pub fn analyze(checkpoint: &Analysis, after: &[(u64, LogRec)]) -> Analysis {
    todo!("4c-c5: start from the checkpoint and let each record change the two tables")
}
