pub fn makesquare(matchsticks: &[u32]) -> bool {
    let mut sticks: Vec<u64> = matchsticks.iter().map(|&m| u64::from(m)).collect();
    let total: u64 = sticks.iter().sum();
    if sticks.len() < 4 || total % 4 != 0 {
        return false;
    }
    sticks.sort_unstable_by(|a, b| b.cmp(a));
    let side = total / 4;
    let mut sides = [0u64; 4];
    for s in sticks {
        match sides.iter_mut().find(|x| **x + s <= side) {
            Some(x) => *x += s,
            None => return false,
        }
    }
    true
}
