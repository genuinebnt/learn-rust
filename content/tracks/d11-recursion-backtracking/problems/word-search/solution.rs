pub fn exist(board: &[&str], word: &str) -> bool {
    fn found(grid: &mut [Vec<u8>], word: &[u8], r: usize, c: usize) -> bool {
        if grid[r][c] != word[0] {
            return false;
        }
        if word.len() == 1 {
            return true;
        }
        let letter = grid[r][c];
        grid[r][c] = 0; // on the current path: matches no letter
        let (h, w, rest) = (grid.len(), grid[0].len(), &word[1..]);
        let hit = (r > 0 && found(grid, rest, r - 1, c))
            || (r + 1 < h && found(grid, rest, r + 1, c))
            || (c > 0 && found(grid, rest, r, c - 1))
            || (c + 1 < w && found(grid, rest, r, c + 1));
        grid[r][c] = letter;
        hit
    }
    let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
    let mut word = word.as_bytes().to_vec();
    // The board must hold every letter at least as often as the word uses it.
    let mut have = [0usize; 256];
    for &b in grid.iter().flatten() {
        have[b as usize] += 1;
    }
    let mut need = [0usize; 256];
    for &b in &word {
        need[b as usize] += 1;
        if need[b as usize] > have[b as usize] {
            return false;
        }
    }
    // Start from the rarer end of the word: fewer starting cells, fewer dead branches.
    if let (Some(&first), Some(&last)) = (word.first(), word.last()) {
        if have[first as usize] > have[last as usize] {
            word.reverse();
        }
    }
    for r in 0..grid.len() {
        for c in 0..grid[r].len() {
            if found(&mut grid, &word, r, c) {
                return true;
            }
        }
    }
    false
}
