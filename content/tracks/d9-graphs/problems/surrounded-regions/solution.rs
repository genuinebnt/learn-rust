pub fn capture_regions(board: &mut [Vec<char>]) {
    let (h, w) = (board.len(), board[0].len());
    // Mark every 'O' reachable from the border as safe, then flip the rest.
    let mut safe = vec![vec![false; w]; h];
    let mut stack: Vec<(usize, usize)> = (0..h)
        .flat_map(|r| [(r, 0), (r, w - 1)])
        .chain((0..w).flat_map(|c| [(0, c), (h - 1, c)]))
        .filter(|&(r, c)| board[r][c] == 'O')
        .collect();
    for &(r, c) in &stack {
        safe[r][c] = true;
    }
    while let Some((r, c)) = stack.pop() {
        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
            if nr < h && nc < w && board[nr][nc] == 'O' && !safe[nr][nc] {
                safe[nr][nc] = true;
                stack.push((nr, nc));
            }
        }
    }
    for r in 0..h {
        for c in 0..w {
            if board[r][c] == 'O' && !safe[r][c] {
                board[r][c] = 'X';
            }
        }
    }
}
