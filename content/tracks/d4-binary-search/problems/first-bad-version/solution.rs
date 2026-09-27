pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
    if n == 0 || !is_bad(n) {
        return None;
    }
    // The answer is in [lo, hi]; hi is known to be bad.
    let (mut lo, mut hi) = (1, n);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if is_bad(mid) {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    Some(lo)
}
