pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
    let mut left = stones.to_vec();
    while left.len() > 1 {
        left.sort_unstable();
        let y = left.pop().unwrap();
        let x = left.pop().unwrap();
        if y > x {
            left.push(y - x);
        }
    }
    left.pop()
}
