pub fn min_eating_speed(piles: &[u32], hours: u64) -> Option<u32> {
    let top = *piles.iter().max()?;
    (1..=top).find(|&k| piles.iter().map(|&p| u64::from(p.div_ceil(k))).sum::<u64>() <= hours)
}
