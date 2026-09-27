/// True if `v` reads the same forwards and backwards.
pub fn is_mirror(v: &[i32]) -> bool {
    let (mut l, mut r) = (0, v.len().saturating_sub(1));
    while l <= r {
        if v[l] != v[r] {
            return false;
        }
        l += 1;
        r -= 1;
    }
    true
}
