pub fn swim_in_water(grid: &[Vec<u32>]) -> u32 {
    let n = grid.len();
    let mut t = grid[0][0].max(grid[n - 1][n - 1]);
    loop {
        let mut seen = vec![vec![false; n]; n];
        seen[0][0] = true;
        let mut stack = vec![(0usize, 0usize)];
        while let Some((r, c)) = stack.pop() {
            for (a, b) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                if a < n && b < n && !seen[a][b] && grid[a][b] <= t {
                    seen[a][b] = true;
                    stack.push((a, b));
                }
            }
        }
        if seen[n - 1][n - 1] {
            return t;
        }
        t += 1;
    }
}
