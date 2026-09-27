pub fn total_n_queens(n: usize) -> usize {
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
    (0..(n + 1) / 2).map(|c| 2 * count(full, 1 << c, 1 << c << 1, 1 << c >> 1)).sum()
}
