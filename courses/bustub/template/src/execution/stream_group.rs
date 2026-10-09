//! Grouping rows that arrive sorted by key.

#[derive(Debug, PartialEq, Eq)]
pub struct NotSorted {
    pub at: usize,
}

/// `(key, sum, count)` per group.
pub fn stream_group_sums(rows: &[(i64, i64)]) -> Result<Vec<(i64, i64, usize)>, NotSorted> {
    todo!("3f-c5: extend the current group while the key repeats; start a new one when it grows; refuse a key that shrinks")
}
