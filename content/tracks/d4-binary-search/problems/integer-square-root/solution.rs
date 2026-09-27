pub fn isqrt(x: u64) -> u64 {
    // Invariant: lo * lo <= x < hi * hi. The root of a u64 is below 2^32.
    let (mut lo, mut hi) = (0u64, x.min(u64::from(u32::MAX)) + 1);
    while hi - lo > 1 {
        let mid = lo + (hi - lo) / 2;
        if mid.checked_mul(mid).is_some_and(|sq| sq <= x) {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    lo
}
