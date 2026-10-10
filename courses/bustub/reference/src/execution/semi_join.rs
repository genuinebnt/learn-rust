//! Semi and anti joins, and the NULL trap of NOT IN.

use std::collections::HashSet;

pub fn semi_join(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    // @begin 3f-c2
    let keys: HashSet<i64> = right.iter().flatten().copied().collect();
    (0..left.len()).filter(|&i| left[i].is_some_and(|k| keys.contains(&k))).collect()
    //~ todo!("3f-c2: left rows with a non-NULL key found among the non-NULL right keys")
    // @end
}

pub fn anti_join(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    // @begin 3f-c2
    let keys: HashSet<i64> = right.iter().flatten().copied().collect();
    (0..left.len()).filter(|&i| !left[i].is_some_and(|k| keys.contains(&k))).collect()
    //~ todo!("3f-c2: left rows with no match (NULL keys never match, so they stay)")
    // @end
}

pub fn not_in(left: &[Option<i64>], right: &[Option<i64>]) -> Vec<usize> {
    // @begin 3f-c2
    if right.is_empty() {
        return (0..left.len()).collect();
    }
    if right.iter().any(|r| r.is_none()) {
        return Vec::new();
    }
    let keys: HashSet<i64> = right.iter().flatten().copied().collect();
    (0..left.len()).filter(|&i| left[i].is_some_and(|k| !keys.contains(&k))).collect()
    //~ todo!("3f-c2: NOT IN: everything for an empty right side, nothing if it has a NULL, else the non-NULL keys that are absent")
    // @end
}
