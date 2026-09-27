pub fn stone_game(piles: &[u32]) -> (u64, u64) {
    let n = piles.len();
    // Maximising your own total is maximising (yours - theirs), because the total is fixed.
    // lead[j] for the current i = the mover's best difference on piles[i..=j].
    let mut lead = vec![0i64; n];
    for i in (0..n).rev() {
        lead[i] = piles[i] as i64;
        for j in i + 1..n {
            lead[j] = (piles[i] as i64 - lead[j]).max(piles[j] as i64 - lead[j - 1]);
        }
    }
    let total: i64 = piles.iter().map(|&p| p as i64).sum();
    let diff = lead.last().copied().unwrap_or(0);
    // alice + bob = total and alice - bob = diff.
    (((total + diff) / 2) as u64, ((total - diff) / 2) as u64)
}
