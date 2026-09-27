pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
    let m = max_choosable as usize;
    if desired_total == 0 {
        return true;
    }
    if m * (m + 1) / 2 < desired_total as usize {
        return false;
    }
    // The set of used numbers fixes the running total too, so it is the whole state.
    // memo[used]: 0 = not solved yet, 1 = the player to move wins, 2 = they lose.
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
