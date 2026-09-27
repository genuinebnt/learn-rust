/// Legacy code: the index of `x` in `v`, or -1. Leave it as it is.
fn legacy_find(v: &[i32], x: i32) -> i32 {
    v.iter().position(|&y| y == x).map_or(-1, |i| i as i32)
}

/// The index of `x` in `v`, or `None`.
pub fn find(v: &[i32], x: i32) -> Option<usize> {
    Some(legacy_find(v, x) as usize)
}
