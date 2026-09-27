/// True if `v` reads the same forwards and backwards.
pub fn is_mirror(v: &[i32]) -> bool {
    let Some(last) = v.len().checked_sub(1) else { return false };
    let (mut l, mut r) = (0, last);
    while l < r {
        if v[l] != v[r] {
            return false;
        }
        l += 1;
        r -= 1;
    }
    true
}
