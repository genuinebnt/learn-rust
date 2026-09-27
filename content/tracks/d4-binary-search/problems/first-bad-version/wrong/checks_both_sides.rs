pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
    let (mut lo, mut hi) = (1u32, n);
    while lo <= hi && hi > 0 {
        let mid = lo + (hi - lo) / 2;
        if is_bad(mid) && (mid == 1 || !is_bad(mid - 1)) {
            return Some(mid);
        }
        if is_bad(mid) {
            hi = mid - 1;
        } else {
            lo = mid + 1;
        }
    }
    None
}
