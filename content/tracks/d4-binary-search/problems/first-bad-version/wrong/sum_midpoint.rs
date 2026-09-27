pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
    if n == 0 || !is_bad(n) {
        return None;
    }
    let (mut lo, mut hi) = (1, n);
    while lo < hi {
        let mid = (lo + hi) / 2;
        if is_bad(mid) {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    Some(lo)
}
