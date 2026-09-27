fn split(lo: u32, hi: u32, cuts: &[u32]) -> u64 {
    let inside: Vec<u32> = cuts.iter().copied().filter(|&c| lo < c && c < hi).collect();
    let mid = (lo + hi) / 2;
    match inside.iter().copied().min_by_key(|&c| c.abs_diff(mid)) {
        None => 0,
        Some(c) => (hi - lo) as u64 + split(lo, c, &inside) + split(c, hi, &inside),
    }
}

pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
    split(0, n, cuts)
}
