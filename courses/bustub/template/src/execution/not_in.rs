//! `x NOT IN (list)` in three-valued logic.

/// `Some(true)`, `Some(false)` or `None` (NULL).
pub fn not_in(x: Option<i64>, list: &[Option<i64>]) -> Option<bool> {
    // "a NULL can never match, so leave NULLs out of the list"
    let known: Vec<i64> = list.iter().flatten().copied().collect();
    match x {
        Some(a) => Some(!known.contains(&a)),
        None => None,
    }
}
