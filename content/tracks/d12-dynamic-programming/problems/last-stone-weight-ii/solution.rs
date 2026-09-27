pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
    // Any smashing order ends as |A - B| for some split of the stones into A and B.
    let total: u32 = stones.iter().sum();
    let half = (total / 2) as usize;
    let mut reach = vec![false; half + 1];
    reach[0] = true;
    for &x in stones {
        let x = x as usize;
        for s in (x..=half).rev() {
            reach[s] = reach[s] || reach[s - x];
        }
    }
    // The lighter pile should be as close to half as possible.
    let best = (0..=half).rev().find(|&s| reach[s]).unwrap_or(0) as u32;
    total - 2 * best
}
