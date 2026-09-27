pub fn shortest_path_binary_matrix(grid: &[Vec<u8>]) -> Option<usize> {
    let n = grid.len();
    let mut d = vec![vec![usize::MAX; n]; n];
    if grid[0][0] == 0 {
        d[0][0] = 1;
    }
    let mut changed = true;
    while changed {
        changed = false;
        for r in 0..n {
            for c in 0..n {
                if grid[r][c] != 0 {
                    continue;
                }
                for a in r.saturating_sub(1)..=(r + 1).min(n - 1) {
                    for b in c.saturating_sub(1)..=(c + 1).min(n - 1) {
                        if d[a][b] != usize::MAX && d[a][b] + 1 < d[r][c] {
                            d[r][c] = d[a][b] + 1;
                            changed = true;
                        }
                    }
                }
            }
        }
    }
    (d[n - 1][n - 1] != usize::MAX).then_some(d[n - 1][n - 1])
}
