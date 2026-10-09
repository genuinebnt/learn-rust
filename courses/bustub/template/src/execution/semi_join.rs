//! Semi and anti joins, and the NULL trap of NOT IN.

use std::collections::HashSet;

pub fn semi_join(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    todo!("3f-c2: left rows with a non-NULL key found among the non-NULL right keys")
}

pub fn anti_join(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    todo!("3f-c2: left rows with no match (NULL keys never match, so they stay)")
}

pub fn not_in(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    todo!("3f-c2: NOT IN: everything for an empty right side, nothing if it has a NULL, else the non-NULL keys that are absent")
}
