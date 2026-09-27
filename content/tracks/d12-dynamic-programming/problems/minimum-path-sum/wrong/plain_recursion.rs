fn cheapest(g: &[Vec<u32>], i: usize, j: usize) -> u64 {
    let here = g[i][j] as u64;
    match (i, j) {
        (0, 0) => here,
        (0, _) => here + cheapest(g, 0, j - 1),
        (_, 0) => here + cheapest(g, i - 1, 0),
        _ => here + cheapest(g, i - 1, j).min(cheapest(g, i, j - 1)),
    }
}

pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
    cheapest(grid, grid.len() - 1, grid[0].len() - 1)
}
