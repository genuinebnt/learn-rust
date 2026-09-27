pub fn isqrt(x: u64) -> u64 {
    let (mut lo, mut hi) = (0u64, x / 2 + 2);
    while hi - lo > 1 {
        let mid = lo + (hi - lo) / 2;
        if mid * mid <= x {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    lo
}
