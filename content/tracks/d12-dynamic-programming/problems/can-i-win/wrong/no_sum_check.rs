pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
    let m = max_choosable as usize;
    if desired_total == 0 {
        return true;
    }
    fn wins(used: usize, left: u32, m: usize, memo: &mut [u8]) -> bool {
        if memo[used] != 0 {
            return memo[used] == 1;
        }
        let win = (0..m).any(|i| {
            let pick = i as u32 + 1;
            used & (1 << i) == 0 && (pick >= left || !wins(used | 1 << i, left - pick, m, memo))
        });
        memo[used] = if win { 1 } else { 2 };
        win
    }
    let mut memo = vec![0u8; 1 << m];
    wins(0, desired_total, m, &mut memo)
}
