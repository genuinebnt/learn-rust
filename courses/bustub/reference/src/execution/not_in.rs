//! `x NOT IN (list)` in three-valued logic.

/// `Some(true)`, `Some(false)` or `None` (NULL).
pub fn not_in(x: Option<i64>, list: &[Option<i64>]) -> Option<bool> {
    // @begin 3i-c2
    if list.iter().any(|v| matches!((x, v), (Some(a), Some(b)) if a == *b)) {
        return Some(false);
    }
    let unknown = (x.is_none() && !list.is_empty()) || list.iter().any(|v| v.is_none());
    if unknown {
        None
    } else {
        Some(true)
    }
    //~ // "a NULL can never match, so leave NULLs out of the list"
    //~ let known: Vec<i64> = list.iter().flatten().copied().collect();
    //~ match x {
    //~     Some(a) => Some(!known.contains(&a)),
    //~     None => None,
    //~ }
    // @end
}
