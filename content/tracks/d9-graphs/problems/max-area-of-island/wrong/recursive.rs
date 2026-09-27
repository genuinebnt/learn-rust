pub fn max_area_of_island(grid: &[Vec<u8>]) -> usize {
    fn area(grid: &[Vec<u8>], seen: &mut Vec<Vec<bool>>, r: usize, c: usize) -> usize {
        if r >= grid.len() || c >= grid[0].len() || grid[r][c] != 1 || seen[r][c] {
            return 0;
        }
        seen[r][c] = true;
        1 + area(grid, seen, r.wrapping_sub(1), c) + area(grid, seen, r + 1, c) + area(grid, seen, r, c.wrapping_sub(1)) + area(grid, seen, r, c + 1)
    }
    let mut seen = vec![vec![false; grid[0].len()]; grid.len()];
    let mut best = 0;
    for r in 0..grid.len() {
        for c in 0..grid[0].len() {
            best = best.max(area(grid, &mut seen, r, c));
        }
    }
    best
}
