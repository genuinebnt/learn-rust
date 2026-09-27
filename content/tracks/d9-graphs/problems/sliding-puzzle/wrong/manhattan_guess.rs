pub fn sliding_puzzle(board: [[u8; 3]; 2]) -> Option<u32> {
    let mut total = 0;
    for r in 0..2 {
        for c in 0..3 {
            let t = board[r][c] as usize;
            let home = if t == 0 { 5 } else { t - 1 };
            total += (r.abs_diff(home / 3) + c.abs_diff(home % 3)) as u32;
        }
    }
    Some(total)
}
