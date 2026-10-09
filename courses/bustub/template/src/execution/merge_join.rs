//! Joining two key-sorted inputs.

/// `(key, payload)` rows, sorted by key. Returns `(left payload, right payload)` for every pair with equal keys, ordered by left row then right row.
pub fn merge_join(left: &[(i64, u32)], right: &[(i64, u32)]) -> Vec<(u32, u32)> {
    todo!("3f-c1: advance the smaller side; on equal keys output the cross product of the two runs of equal keys")
}
