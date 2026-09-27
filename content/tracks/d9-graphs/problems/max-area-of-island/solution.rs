pub fn max_area_of_island(grid: &[Vec<u8>]) -> usize {
    let (h, w) = (grid.len(), grid.first().map_or(0, Vec::len));
    let mut seen = vec![vec![false; w]; h];
    let mut best = 0;
    for r0 in 0..h {
        for c0 in 0..w {
            if grid[r0][c0] != 1 || seen[r0][c0] {
                continue;
            }
            seen[r0][c0] = true;
            let mut stack = vec![(r0, c0)];
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
            best = best.max(area);
        }
    }
    best
}
