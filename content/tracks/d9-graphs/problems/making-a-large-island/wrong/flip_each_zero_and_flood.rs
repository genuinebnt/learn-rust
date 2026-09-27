pub fn largest_island(grid: &[Vec<u8>]) -> usize {
    let (h, w) = (grid.len(), grid[0].len());
    let mut best = 0;
    let mut any_water = false;
    let mut seen = vec![vec![0usize; w]; h];
    let mut round = 0;
    for r in 0..h {
        for c in 0..w {
            if grid[r][c] != 0 {
                continue;
            }
            any_water = true;
            round += 1;
            seen[r][c] = round;
            let mut stack = vec![(r, c)];
            let mut count = 0;
            while let Some((y, x)) = stack.pop() {
                count += 1;
                for (ny, nx) in [(y.wrapping_sub(1), x), (y + 1, x), (y, x.wrapping_sub(1)), (y, x + 1)] {
                    if ny < h && nx < w && grid[ny][nx] == 1 && seen[ny][nx] != round {
                        seen[ny][nx] = round;
                        stack.push((ny, nx));
                    }
                }
            }
            best = best.max(count);
        }
    }
    if any_water { best } else { h * w }
}
