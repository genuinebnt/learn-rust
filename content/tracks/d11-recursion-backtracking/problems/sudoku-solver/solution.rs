pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
    const DIGITS: u16 = 0b11_1111_1110; // bits 1 to 9

    fn box_of(r: usize, c: usize) -> usize {
        r / 3 * 3 + c / 3
    }

    // used[0][row], used[1][column], used[2][box]: bit d is set when digit d is already there.
    fn search(board: &mut [[u8; 9]; 9], used: &mut [[u16; 9]; 3]) -> bool {
        // The empty cell with the fewest candidates. One candidate is forced, none is a dead end: stop looking.
        let mut best: Option<(usize, usize, u16)> = None;
        'scan: for r in 0..9 {
            for c in 0..9 {
                if board[r][c] != 0 {
                    continue;
                }
                let free = DIGITS & !(used[0][r] | used[1][c] | used[2][box_of(r, c)]);
                if best.is_none_or(|(_, _, f)| free.count_ones() < f.count_ones()) {
                    best = Some((r, c, free));
                    if free.count_ones() <= 1 {
                        break 'scan;
                    }
                }
            }
        }
        let Some((r, c, mut free)) = best else {
            return true; // no empty cell left
        };
        let units = [(0, r), (1, c), (2, box_of(r, c))];
        while free != 0 {
            let bit = free & free.wrapping_neg();
            free ^= bit;
            board[r][c] = bit.trailing_zeros() as u8;
            for (u, i) in units {
                used[u][i] ^= bit;
            }
            if search(board, used) {
                return true;
            }
            for (u, i) in units {
                used[u][i] ^= bit;
            }
        }
        board[r][c] = 0; // leave the cell as it was found
        false
    }

    let mut used = [[0u16; 9]; 3];
    for (r, row) in board.iter().enumerate() {
        for (c, &d) in row.iter().enumerate() {
            if d == 0 {
                continue;
            }
            let bit = 1 << d;
            let units = [(0, r), (1, c), (2, box_of(r, c))];
            if units.iter().any(|&(u, i)| used[u][i] & bit != 0) {
                return false; // two givens clash
            }
            for (u, i) in units {
                used[u][i] |= bit;
            }
        }
    }
    search(board, &mut used)
}
