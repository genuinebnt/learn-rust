pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {
    let (h, w) = (heights.len(), heights[0].len());
    let mut limits = vec![0];
    for r in 0..h {
        for c in 0..w {
            if r + 1 < h {
                limits.push(heights[r][c].abs_diff(heights[r + 1][c]));
            }
            if c + 1 < w {
                limits.push(heights[r][c].abs_diff(heights[r][c + 1]));
            }
        }
    }
    limits.sort_unstable();
    limits.dedup();
    for limit in limits {
        let mut seen = vec![vec![false; w]; h];
        seen[0][0] = true;
        let mut stack = vec![(0usize, 0usize)];
        while let Some((r, c)) = stack.pop() {
            for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                if nr < h && nc < w && !seen[nr][nc] && heights[r][c].abs_diff(heights[nr][nc]) <= limit {
                    seen[nr][nc] = true;
                    stack.push((nr, nc));
                }
            }
        }
        if seen[h - 1][w - 1] {
            return limit;
        }
    }
    unreachable!()
}
