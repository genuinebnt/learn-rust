pub fn island_perimeter(grid: &[Vec<u8>]) -> usize {
    let (h, w) = (grid.len(), grid[0].len());
    let mut sides = 0;
    for r in 0..h {
        for c in 0..w {
            if grid[r][c] == 1 {
                for (a, b) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if a < h && b < w && grid[a][b] == 0 {
                        sides += 1;
                    }
                }
            }
        }
    }
    sides
}
