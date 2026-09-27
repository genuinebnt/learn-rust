pub fn unique_paths_with_obstacles(grid: &[Vec<u8>]) -> u64 {
    let (m, n) = (grid.len(), grid[0].len());
    let mut paths = vec![vec![0u64; n]; m];
    for i in 0..m {
        for j in 0..n {
            paths[i][j] = if grid[i][j] == 1 {
                0
            } else if i == 0 || j == 0 {
                1
            } else {
                paths[i - 1][j] + paths[i][j - 1]
            };
        }
    }
    paths[m - 1][n - 1]
}
