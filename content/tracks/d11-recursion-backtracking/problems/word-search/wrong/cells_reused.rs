pub fn exist(board: &[&str], word: &str) -> bool {
    fn found(grid: &[&[u8]], word: &[u8], r: usize, c: usize) -> bool {
        if grid[r][c] != word[0] {
            return false;
        }
        if word.len() == 1 {
            return true;
        }
        let (h, w, rest) = (grid.len(), grid[0].len(), &word[1..]);
        (r > 0 && found(grid, rest, r - 1, c))
            || (r + 1 < h && found(grid, rest, r + 1, c))
            || (c > 0 && found(grid, rest, r, c - 1))
            || (c + 1 < w && found(grid, rest, r, c + 1))
    }
    let grid: Vec<&[u8]> = board.iter().map(|row| row.as_bytes()).collect();
    let mut have = [0usize; 256];
    for &b in grid.iter().copied().flatten() {
        have[b as usize] += 1;
    }
    if word.bytes().any(|b| have[b as usize] == 0) {
        return false;
    }
    (0..grid.len()).any(|r| (0..grid[r].len()).any(|c| found(&grid, word.as_bytes(), r, c)))
}
