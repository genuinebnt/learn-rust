pub fn makesquare(matchsticks: &[u32]) -> bool {
    fn place(sticks: &[u64], sides: &mut [u64; 4], side: u64) -> bool {
        let Some((&stick, rest)) = sticks.split_first() else {
            return true; // every stick placed and no side over `side`: all four are exactly `side`
        };
        for i in 0..4 {
            // A side as long as an earlier one would repeat that side's subtree.
            if sides[i] + stick > side || sides[..i].contains(&sides[i]) {
                continue;
            }
            sides[i] += stick;
            if place(rest, sides, side) {
                return true;
            }
            sides[i] -= stick;
        }
        false
    }
    let mut sticks: Vec<u64> = matchsticks.iter().map(|&m| u64::from(m)).collect();
    let total: u64 = sticks.iter().sum();
    if sticks.len() < 4 || !total.is_multiple_of(4) {
        return false;
    }
    // Longest first: they have the fewest places to go, so a dead end shows up near the root.
    sticks.sort_unstable_by(|a, b| b.cmp(a));
    let side = total / 4;
    sticks[0] <= side && place(&sticks, &mut [0; 4], side)
}
