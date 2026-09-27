fn count(g: &[Vec<u8>], i: usize, j: usize) -> u64 {
    if g[i][j] == 1 {
        return 0;
    }
    if i == 0 && j == 0 {
        return 1;
    }
    (if i > 0 { count(g, i - 1, j) } else { 0 }) + (if j > 0 { count(g, i, j - 1) } else { 0 })
}

pub fn unique_paths_with_obstacles(grid: &[Vec<u8>]) -> u64 {
    count(grid, grid.len() - 1, grid[0].len() - 1)
}
