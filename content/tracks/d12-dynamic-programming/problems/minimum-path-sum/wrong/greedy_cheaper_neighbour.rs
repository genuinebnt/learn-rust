pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
    let (m, n) = (grid.len(), grid[0].len());
    let (mut i, mut j) = (0, 0);
    let mut total = grid[0][0] as u64;
    while (i, j) != (m - 1, n - 1) {
        if i == m - 1 {
            j += 1;
        } else if j == n - 1 || grid[i + 1][j] <= grid[i][j + 1] {
            i += 1;
        } else {
            j += 1;
        }
        total += grid[i][j] as u64;
    }
    total
}
