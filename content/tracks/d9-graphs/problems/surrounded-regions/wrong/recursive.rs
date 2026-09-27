pub fn capture_regions(board: &mut [Vec<char>]) {
    fn mark(board: &mut [Vec<char>], r: usize, c: usize) {
        if r >= board.len() || c >= board[0].len() || board[r][c] != 'O' {
            return;
        }
        board[r][c] = 'S';
        mark(board, r.wrapping_sub(1), c);
        mark(board, r + 1, c);
        mark(board, r, c.wrapping_sub(1));
        mark(board, r, c + 1);
    }
    let (h, w) = (board.len(), board[0].len());
    for r in 0..h {
        mark(board, r, 0);
        mark(board, r, w - 1);
    }
    for c in 0..w {
        mark(board, 0, c);
        mark(board, h - 1, c);
    }
    for row in board.iter_mut() {
        for ch in row.iter_mut() {
            *ch = if *ch == 'S' { 'O' } else { 'X' };
        }
    }
}
