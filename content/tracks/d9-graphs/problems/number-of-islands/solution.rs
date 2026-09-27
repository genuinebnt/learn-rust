pub fn num_islands(grid: &[&str]) -> usize {
    let rows: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
    let (h, w) = (rows.len(), rows.first().map_or(0, |r| r.len()));
    let mut seen = vec![vec![false; w]; h];
    let mut count = 0;
    for r0 in 0..h {
        for c0 in 0..w {
            if rows[r0][c0] != b'1' || seen[r0][c0] {
                continue;
            }
            count += 1;
            seen[r0][c0] = true;
            let mut stack = vec![(r0, c0)];
            while let Some((r, c)) = stack.pop() {
                for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                    if nr < h && nc < w && rows[nr][nc] == b'1' && !seen[nr][nc] {
                        seen[nr][nc] = true;
                        stack.push((nr, nc));
                    }
                }
            }
        }
    }
    count
}
