pub fn total_n_queens(n: usize) -> usize {
    // `cols`, `diag`, `anti`: the columns of the next row attacked from above (see N-Queens).
    fn count(full: u16, cols: u16, diag: u16, anti: u16) -> usize {
        if cols == full {
            return 1;
        }
        let mut free = full & !(cols | diag | anti);
        let mut total = 0;
        while free != 0 {
            let bit = free & free.wrapping_neg();
            free ^= bit;
            total += count(full, cols | bit, (diag | bit) << 1, (anti | bit) >> 1);
        }
        total
    }
    let full = ((1u32 << n) - 1) as u16;
    let first_row = |c: usize| {
        let bit = 1u16 << c;
        count(full, bit, bit << 1, bit >> 1)
    };
    // The mirror image of a solution is a solution: count the left half of the first row twice,
    // and the middle column (odd n) once.
    let half: usize = (0..n / 2).map(first_row).sum();
    2 * half + if n % 2 == 1 { first_row(n / 2) } else { 0 }
}
