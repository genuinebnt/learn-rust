use std::collections::BTreeSet;

pub fn nearest(prices: &BTreeSet<u32>, x: u32) -> (Option<u32>, Option<u32>) {
    let floor = prices.range(..=x).next_back().copied();
    let ceiling = prices.range(x..).next().copied();
    (floor, ceiling)
}
