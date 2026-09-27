/// The size of every island of 1s, in the order their first cells appear row by row.
pub fn island_sizes(mut grid: Vec<Vec<u8>>) -> Vec<usize> {
    let (h, w) = (grid.len(), grid.first().map_or(0, Vec::len));
    fn sink_island(grid: &mut [Vec<u8>], r: usize, c: usize) -> usize {
        if r >= grid.len() || c >= grid[r].len() || grid[r][c] == 0 {
            return 0;
        }
        grid[r][c] = 0;
        let mut size = 1;
        for (dr, dc) in [(-1i32, -1i32), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] {
            size += sink_island(grid, (r as i32 + dr) as usize, (c as i32 + dc) as usize);
        }
        size
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
