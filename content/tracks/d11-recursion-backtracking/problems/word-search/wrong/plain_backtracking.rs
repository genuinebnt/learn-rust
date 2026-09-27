pub fn exist(board: &[&str], word: &str) -> bool {
    fn found(grid: &mut [Vec<u8>], word: &[u8], r: usize, c: usize) -> bool {
        if grid[r][c] != word[0] {
            return false;
        }
        if word.len() == 1 {
            return true;
        }
        let letter = grid[r][c];
        grid[r][c] = 0;
        let (h, w, rest) = (grid.len(), grid[0].len(), &word[1..]);
        let hit = (r > 0 && found(grid, rest, r - 1, c))
            || (r + 1 < h && found(grid, rest, r + 1, c))
            || (c > 0 && found(grid, rest, r, c - 1))
            || (c + 1 < w && found(grid, rest, r, c + 1));
        grid[r][c] = letter;
        hit
    }
    let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
    if word.len() > grid.len() * grid[0].len() {
        return false;
    }
    for r in 0..grid.len() {
        for c in 0..grid[r].len() {
            if found(&mut grid, word.as_bytes(), r, c) {
                return true;
            }
        }
    }
    false
}
