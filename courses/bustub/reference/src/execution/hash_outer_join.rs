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
    // @begin 3j-c1
    let mut table: HashMap<i64, Vec<usize>> = HashMap::new();
    for (i, (key, _)) in right.iter().enumerate() {
        if let Some(k) = key {
            table.entry(*k).or_default().push(i);
        }
    }
    let mut matched = vec![false; right.len()];
    let mut out = Vec::new();
    for (key, payload) in left {
        match (*key).and_then(|k| table.get(&k)) {
            Some(partners) => {
                for &i in partners {
                    matched[i] = true;
                    out.push((Some(*payload), Some(right[i].1)));
                }
            }
            None => {
                if matches!(kind, JoinKind::Left | JoinKind::Full) {
                    out.push((Some(*payload), None));
                }
            }
        }
    }
    if matches!(kind, JoinKind::Right | JoinKind::Full) {
        for (i, (_, payload)) in right.iter().enumerate() {
            if !matched[i] {
                out.push((None, Some(*payload)));
            }
        }
    }
    out
    //~ let _ = (left, right, kind, HashMap::<i64, usize>::new());
    //~ todo!("3j-c1: build a hash table on the right keys, probe it with the left rows, flag the right rows that were hit")
    // @end
}
