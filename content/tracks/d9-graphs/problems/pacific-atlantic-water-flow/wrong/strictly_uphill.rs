pub fn pacific_atlantic(heights: &[Vec<u32>]) -> Vec<(usize, usize)> {
    let (h, w) = (heights.len(), heights[0].len());
    let climb = |starts: Vec<(usize, usize)>| {
        let mut seen = vec![vec![false; w]; h];
        for &(r, c) in &starts {
            seen[r][c] = true;
        }
        let mut stack = starts;
        while let Some((r, c)) = stack.pop() {
            for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                if nr < h && nc < w && !seen[nr][nc] && heights[nr][nc] > heights[r][c] {
                    seen[nr][nc] = true;
                    stack.push((nr, nc));
                }
            }
        }
        seen
    };
    let pacific = climb((0..h).map(|r| (r, 0)).chain((0..w).map(|c| (0, c))).collect());
    let atlantic = climb((0..h).map(|r| (r, w - 1)).chain((0..w).map(|c| (h - 1, c))).collect());
    (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).filter(|&(r, c)| pacific[r][c] && atlantic[r][c]).collect()
}
