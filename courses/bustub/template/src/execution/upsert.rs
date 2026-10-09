//! INSERT ... ON CONFLICT over a keyed table.

use std::collections::BTreeMap;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Conflict {
    DoNothing,
    Replace,
    Add,
}

#[derive(Debug, PartialEq, Eq, Default)]
pub struct Counts {
    pub inserted: usize,
    pub updated: usize,
    pub ignored: usize,
}

pub fn upsert(table: &mut BTreeMap<i64, i64>, rows: &[(i64, i64)], policy: Conflict) -> Counts {
    todo!("3e-c2: apply the rows in order, counting what happened to each")
}
