pub fn min_eating_speed(piles: &[u32], hours: u64) -> Option<u32> {
    if piles.is_empty() || (piles.len() as u64) > hours {
        return None;
    }
    let needed = |k: u32| piles.iter().map(|&p| p.div_ceil(k)).sum::<u32>();
    let (mut lo, mut hi) = (1, *piles.iter().max()?);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if u64::from(needed(mid)) <= hours {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    Some(lo)
}
