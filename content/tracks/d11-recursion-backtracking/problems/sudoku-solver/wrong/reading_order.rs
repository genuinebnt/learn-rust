pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
    fn box_of(r: usize, c: usize) -> usize {
        r / 3 * 3 + c / 3
    }
    fn search(board: &mut [[u8; 9]; 9], i: usize, used: &mut [[u16; 9]; 3]) -> bool {
        if i == 81 {
            return true;
        }
        let (r, c) = (i / 9, i % 9);
        if board[r][c] != 0 {
            return search(board, i + 1, used);
        }
        for d in 1..=9u8 {
            let bit = 1u16 << d;
            if (used[0][r] | used[1][c] | used[2][box_of(r, c)]) & bit != 0 {
                continue;
            }
            board[r][c] = d;
            used[0][r] ^= bit;
            used[1][c] ^= bit;
            used[2][box_of(r, c)] ^= bit;
            if search(board, i + 1, used) {
                return true;
            }
            used[0][r] ^= bit;
            used[1][c] ^= bit;
            used[2][box_of(r, c)] ^= bit;
        }
        board[r][c] = 0;
        false
    }
    let mut used = [[0u16; 9]; 3];
    for r in 0..9 {
        for c in 0..9 {
            let d = board[r][c];
            if d == 0 {
                continue;
            }
            let bit = 1 << d;
            if (used[0][r] | used[1][c] | used[2][box_of(r, c)]) & bit != 0 {
                return false;
            }
            used[0][r] |= bit;
            used[1][c] |= bit;
            used[2][box_of(r, c)] |= bit;
        }
    }
    search(board, 0, &mut used)
}
