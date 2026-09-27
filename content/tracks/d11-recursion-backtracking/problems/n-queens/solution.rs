pub fn solve_n_queens(n: usize) -> Vec<Vec<String>> {
    // Bit c of each mask is column c of the row being filled. `cols`: columns already taken. `diag` / `anti`:
    // squares attacked along the two diagonals by the queens above.
    fn place(full: u16, cols: u16, diag: u16, anti: u16, queens: &mut Vec<usize>, out: &mut Vec<Vec<String>>) {
        if cols == full {
            let n = queens.len();
            out.push(queens.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect());
            return;
        }
        let mut free = full & !(cols | diag | anti);
        while free != 0 {
            let bit = free & free.wrapping_neg(); // the lowest free column
            free ^= bit;
            queens.push(bit.trailing_zeros() as usize);
            // One row down, a diagonal attack moves one column right (<< 1), an anti-diagonal one left (>> 1).
            place(full, cols | bit, (diag | bit) << 1, (anti | bit) >> 1, queens, out);
            queens.pop();
        }
    }
    let full = ((1u32 << n) - 1) as u16;
    let mut out = Vec::new();
    place(full, 0, 0, 0, &mut Vec::with_capacity(n), &mut out);
    out
}
