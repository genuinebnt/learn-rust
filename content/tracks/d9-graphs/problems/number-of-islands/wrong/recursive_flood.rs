pub fn num_islands(grid: &[&str]) -> usize {
    fn sink(rows: &[&[u8]], seen: &mut Vec<Vec<bool>>, r: usize, c: usize) {
        if r >= rows.len() || c >= rows[r].len() || rows[r][c] != b'1' || seen[r][c] {
            return;
        }
        seen[r][c] = true;
        sink(rows, seen, r.wrapping_sub(1), c);
        sink(rows, seen, r + 1, c);
        sink(rows, seen, r, c.wrapping_sub(1));
        sink(rows, seen, r, c + 1);
    }

    let rows: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
    let w = rows.first().map_or(0, |r| r.len());
    let mut seen = vec![vec![false; w]; rows.len()];
    let mut count = 0;
    for r in 0..rows.len() {
        for c in 0..w {
            if rows[r][c] == b'1' && !seen[r][c] {
                count += 1;
                sink(&rows, &mut seen, r, c);
            }
        }
    }
    count
}
