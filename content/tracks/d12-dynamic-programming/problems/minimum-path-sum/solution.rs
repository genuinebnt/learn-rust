pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
    let n = grid[0].len();
    // best[j] = cheapest path to (i, j). Before the first row only the start is reachable.
    let mut best = vec![u64::MAX; n];
    best[0] = 0;
    for row in grid {
        for j in 0..n {
            let from = if j > 0 { best[j].min(best[j - 1]) } else { best[0] };
            best[j] = from + row[j] as u64;
        }
    }
    best[n - 1]
}
