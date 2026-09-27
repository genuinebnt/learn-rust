pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {
    let (h, w) = (heights.len(), heights[0].len());
    let mut best = vec![vec![u32::MAX; w]; h];
    best[0][0] = 0;
    for r in 0..h {
        for c in 0..w {
            if r > 0 {
                best[r][c] = best[r][c].min(best[r - 1][c].max(heights[r][c].abs_diff(heights[r - 1][c])));
            }
            if c > 0 {
                best[r][c] = best[r][c].min(best[r][c - 1].max(heights[r][c].abs_diff(heights[r][c - 1])));
            }
        }
    }
    best[h - 1][w - 1]
}
