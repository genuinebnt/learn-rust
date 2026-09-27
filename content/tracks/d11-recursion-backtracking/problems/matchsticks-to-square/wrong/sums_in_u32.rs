pub fn makesquare(matchsticks: &[u32]) -> bool {
    fn place(sticks: &[u32], sides: &mut [u32; 4], side: u32) -> bool {
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
    let mut sticks = matchsticks.to_vec();
    let total: u32 = sticks.iter().sum();
    if sticks.len() < 4 || total % 4 != 0 {
        return false;
    }
    sticks.sort_unstable_by(|a, b| b.cmp(a));
    let side = total / 4;
    sticks[0] <= side && place(&sticks, &mut [0; 4], side)
}
