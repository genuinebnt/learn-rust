pub fn max_area_of_island(grid: &[Vec<u8>]) -> usize {
    let (h, w) = (grid.len(), grid[0].len());
    let Some(start) = (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).find(|&(r, c)| grid[r][c] == 1) else {
        return 0;
    };
    let mut seen = vec![vec![false; w]; h];
    seen[start.0][start.1] = true;
    let mut stack = vec![start];
    let mut area = 0;
    while let Some((r, c)) = stack.pop() {
        area += 1;
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < h && nc < w && grid[nr][nc] == 1 && !seen[nr][nc] {
                seen[nr][nc] = true;
                stack.push((nr, nc));
            }
        }
    }
    area
}
