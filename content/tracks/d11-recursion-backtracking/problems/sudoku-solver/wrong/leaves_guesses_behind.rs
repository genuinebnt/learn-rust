pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
    const DIGITS: u16 = 0b11_1111_1110;
    fn box_of(r: usize, c: usize) -> usize {
        r / 3 * 3 + c / 3
    }
    fn search(board: &mut [[u8; 9]; 9], used: &mut [[u16; 9]; 3]) -> bool {
        let mut best: Option<(usize, usize, u16)> = None;
        for r in 0..9 {
            for c in 0..9 {
                if board[r][c] != 0 {
                    continue;
                }
                let free = DIGITS & !(used[0][r] | used[1][c] | used[2][box_of(r, c)]);
                if best.is_none_or(|(_, _, f)| free.count_ones() < f.count_ones()) {
                    best = Some((r, c, free));
                }
            }
        }
        let Some((r, c, mut free)) = best else {
            return true;
        };
        let units = [(0, r), (1, c), (2, box_of(r, c))];
        // Search a copy of the masks, so there's nothing to undo in them.
        while free != 0 {
            let bit = free & free.wrapping_neg();
            free ^= bit;
            board[r][c] = bit.trailing_zeros() as u8;
            let mut next = *used;
            for (u, i) in units {
                next[u][i] |= bit;
            }
            if search(board, &mut next) {
                return true;
            }
        }
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
            let units = [(0, r), (1, c), (2, box_of(r, c))];
            if units.iter().any(|&(u, i)| used[u][i] & bit != 0) {
                return false;
            }
            for (u, i) in units {
                used[u][i] |= bit;
            }
        }
    }
    search(board, &mut used)
}
