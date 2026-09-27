fn cheapest(pts: &[u64]) -> u64 {
    if pts.len() <= 2 {
        return 0;
    }
    let len = pts[pts.len() - 1] - pts[0];
    (1..pts.len() - 1).map(|k| len + cheapest(&pts[..=k]) + cheapest(&pts[k..])).min().unwrap()
}

pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
    let mut pts: Vec<u64> = cuts.iter().map(|&c| c as u64).collect();
    pts.push(0);
    pts.push(n as u64);
    pts.sort_unstable();
    cheapest(&pts)
}
