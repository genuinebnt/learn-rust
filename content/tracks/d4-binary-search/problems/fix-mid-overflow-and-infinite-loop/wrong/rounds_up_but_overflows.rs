/// The largest x in lo..=hi with pred(x) true, or None if pred(lo) is false.
/// pred must be true up to some point and false after it.
pub fn last_true(lo: u32, hi: u32, pred: impl Fn(u32) -> bool) -> Option<u32> {
    if !pred(lo) {
        return None;
    }
    let (mut lo, mut hi) = (lo, hi);
    while lo < hi {
        let mid = (lo + hi + 1) / 2;
        if pred(mid) {
            lo = mid;
        } else {
            hi = mid - 1;
        }
    }
    Some(lo)
}
