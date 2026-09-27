pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
    let m = max_choosable as usize;
    if desired_total == 0 {
        return true;
    }
    if m * (m + 1) / 2 < desired_total as usize {
        return false;
    }
    // Remembers the answer per remaining total, forgetting which numbers are used.
    fn wins(used: usize, left: u32, m: usize, memo: &mut [u8]) -> bool {
        if memo[left as usize] != 0 {
            return memo[left as usize] == 1;
        }
        let win = (0..m).any(|i| {
            let pick = i as u32 + 1;
            used & (1 << i) == 0 && (pick >= left || !wins(used | 1 << i, left - pick, m, memo))
        });
        memo[left as usize] = if win { 1 } else { 2 };
        win
    }
    let mut memo = vec![0u8; desired_total as usize + 1];
    wins(0, desired_total, m, &mut memo)
}
