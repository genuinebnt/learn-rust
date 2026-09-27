pub fn makesquare(matchsticks: &[u32]) -> bool {
    fn place(sticks: &[u64], sides: &mut [u64; 4], side: u64) -> bool {
        let Some((&stick, rest)) = sticks.split_first() else {
            return true;
        };
        for i in 0..4 {
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
    let sticks: Vec<u64> = matchsticks.iter().map(|&m| u64::from(m)).collect();
    let total: u64 = sticks.iter().sum();
    if sticks.len() < 4 || total % 4 != 0 {
        return false;
    }
    let side = total / 4;
    sticks.iter().all(|&s| s <= side) && place(&sticks, &mut [0; 4], side)
}
