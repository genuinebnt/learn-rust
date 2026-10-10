//! Joining two key-sorted inputs.

/// `(key, payload)` rows, sorted by key. Returns `(left payload, right payload)` for every pair with equal keys, ordered by left row then right row.
pub fn merge_join(left: &[(i64, u32)], right: &[(i64, u32)]) -> Vec<(u32, u32)> {
    // @begin 3f-c1
    let mut out = Vec::new();
    let (mut i, mut j) = (0, 0);
    while i < left.len() && j < right.len() {
        match left[i].0.cmp(&right[j].0) {
            std::cmp::Ordering::Less => i += 1,
            std::cmp::Ordering::Greater => j += 1,
            std::cmp::Ordering::Equal => {
                let key = left[i].0;
                let j_end = j + right[j..].iter().take_while(|r| r.0 == key).count();
                while i < left.len() && left[i].0 == key {
                    for r in &right[j..j_end] {
                        out.push((left[i].1, r.1));
                    }
                    i += 1;
                }
                j = j_end;
            }
        }
    }
    out
    //~ todo!("3f-c1: advance the smaller side; on equal keys output the cross product of the two runs of equal keys")
    // @end
}
