pub fn solve_n_queens(n: usize) -> Vec<Vec<String>> {
    fn place(full: u16, cols: u16, diag: u16, queens: &mut Vec<usize>, out: &mut Vec<Vec<String>>) {
        if cols == full {
            let n = queens.len();
            out.push(queens.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect());
            return;
        }
        let mut free = full & !(cols | diag);
        while free != 0 {
            let bit = free & free.wrapping_neg();
            free ^= bit;
            queens.push(bit.trailing_zeros() as usize);
            place(full, cols | bit, (diag | bit) << 1, queens, out);
            queens.pop();
        }
    }
    let full = ((1u32 << n) - 1) as u16;
    let mut out = Vec::new();
    place(full, 0, 0, &mut Vec::new(), &mut out);
    out
}
