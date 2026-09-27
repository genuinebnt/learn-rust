pub fn pacific_atlantic(heights: &[Vec<u32>]) -> Vec<(usize, usize)> {
    let (h, w) = (heights.len(), heights[0].len());
    let mut out = Vec::new();
    for r in 0..h {
        for c in 0..w {
            let mut seen = vec![vec![false; w]; h];
            seen[r][c] = true;
            let mut stack = vec![(r, c)];
            let (mut pacific, mut atlantic) = (false, false);
            while let Some((a, b)) = stack.pop() {
                pacific |= a == 0 || b == 0;
                atlantic |= a == h - 1 || b == w - 1;
                if pacific && atlantic {
                    break;
                }
                for (x, y) in [(a.wrapping_sub(1), b), (a + 1, b), (a, b.wrapping_sub(1)), (a, b + 1)] {
                    if x < h && y < w && !seen[x][y] && heights[x][y] <= heights[a][b] {
                        seen[x][y] = true;
                        stack.push((x, y));
                    }
                }
            }
            if pacific && atlantic {
                out.push((r, c));
            }
        }
    }
    out
}
