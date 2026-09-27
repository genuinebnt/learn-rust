use std::collections::BTreeSet;

pub fn nearest(prices: &BTreeSet<u32>, x: u32) -> (Option<u32>, Option<u32>) {
    let floor = prices.iter().copied().filter(|&p| p <= x).max();
    let ceiling = prices.iter().copied().filter(|&p| p >= x).min();
    (floor, ceiling)
}
