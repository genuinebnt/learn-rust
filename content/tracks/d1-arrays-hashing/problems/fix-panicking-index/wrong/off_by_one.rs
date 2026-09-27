/// The element at `i`, or 0 when `i` is past the end.
pub fn nth_or_zero(v: &[i32], i: usize) -> i32 {
    if i + 1 < v.len() { v[i] } else { 0 }
}
