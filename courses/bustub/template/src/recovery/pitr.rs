//! Recovering the database as of a log position.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Rec {
    Begin(u32),
    Set(u32, i64, i64),
    Commit(u32),
    Abort(u32),
}

/// `log` is `(lsn, record)` in increasing LSN order.
pub fn recover_until(log: &[(u64, Rec)], upto_lsn: u64) -> BTreeMap<i64, i64> {
    todo!("4c-c4: find the transactions committed by the point; apply only their writes, in log order")
}
