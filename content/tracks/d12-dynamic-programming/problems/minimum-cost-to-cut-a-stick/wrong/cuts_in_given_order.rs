pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
    let mut pieces: Vec<(u32, u32)> = vec![(0, n)];
    let mut total = 0u64;
    for &c in cuts {
        let k = pieces.iter().position(|&(a, b)| a < c && c < b).unwrap();
        let (a, b) = pieces.swap_remove(k);
        total += (b - a) as u64;
        pieces.push((a, c));
        pieces.push((c, b));
    }
    total
}
