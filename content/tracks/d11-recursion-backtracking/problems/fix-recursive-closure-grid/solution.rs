/// The size of every island of 1s, in the order their first cells appear row by row.
pub fn island_sizes(mut grid: Vec<Vec<u8>>) -> Vec<usize> {
    let (h, w) = (grid.len(), grid.first().map_or(0, Vec::len));
    // Sinks the island through (r, c) and returns how many cells it had.
    fn sink_island(grid: &mut [Vec<u8>], r: usize, c: usize) -> usize {
        if r >= grid.len() || c >= grid[r].len() || grid[r][c] == 0 {
            return 0;
        }
        grid[r][c] = 0;
        1 + sink_island(grid, r + 1, c) + sink_island(grid, r.wrapping_sub(1), c) + sink_island(grid, r, c + 1) + sink_island(grid, r, c.wrapping_sub(1))
    }
    let mut sizes = Vec::new();
    for r in 0..h {
        for c in 0..w {
            if grid[r][c] == 1 {
                sizes.push(sink_island(&mut grid, r, c));
            }
        }
    }
    sizes
}
