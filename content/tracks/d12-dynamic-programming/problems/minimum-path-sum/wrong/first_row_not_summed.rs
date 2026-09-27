pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
    let (m, n) = (grid.len(), grid[0].len());
    let mut best = vec![vec![0u64; n]; m];
    for i in 0..m {
        for j in 0..n {
            let here = grid[i][j] as u64;
            best[i][j] = match (i, j) {
                (0, _) => here,
                (_, 0) => here + best[i - 1][0],
                _ => here + best[i - 1][j].min(best[i][j - 1]),
            };
        }
    }
    best[m - 1][n - 1]
}
