pub fn swim_in_water(grid: &[Vec<u32>]) -> u32 {
    let n = grid.len();
    let mut best = vec![vec![u32::MAX; n]; n];
    for r in 0..n {
        for c in 0..n {
            let from = if r == 0 && c == 0 { 0 } else {
                let up = if r > 0 { best[r - 1][c] } else { u32::MAX };
                let left = if c > 0 { best[r][c - 1] } else { u32::MAX };
                up.min(left)
            };
            best[r][c] = from.max(grid[r][c]);
        }
    }
    best[n - 1][n - 1]
}
