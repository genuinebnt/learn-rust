pub fn capture_regions(board: &mut [Vec<char>]) {
    let (h, w) = (board.len(), board[0].len());
    for r in 1..h.saturating_sub(1) {
        for c in 1..w.saturating_sub(1) {
            board[r][c] = 'X';
        }
    }
}
