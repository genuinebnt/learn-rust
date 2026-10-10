//! Joins on equal keys with a hash table.

use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum JoinKind {
    Inner,
    Left,
    Right,
    Full,
}

/// A row: a join key that may be NULL, and a payload.
pub type Row = (Option<i64>, i64);

/// The pairs `(left payload, right payload)` of `left JOIN right ON left.key = right.key`; `None` is NULL padding.
pub fn hash_join(left: &[Row], right: &[Row], kind: JoinKind) -> Vec<(Option<i64>, Option<i64>)> {
    let _ = (left, right, kind, HashMap::<i64, usize>::new());
    todo!("3j-c1: build a hash table on the right keys, probe it with the left rows, flag the right rows that were hit")
}
