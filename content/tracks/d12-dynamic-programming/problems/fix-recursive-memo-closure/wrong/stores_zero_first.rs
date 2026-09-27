use std::collections::HashMap;

fn count(n: u64, memo: &mut HashMap<u64, u64>) -> u64 {
    if n < 3 {
        return [1, 1, 2][n as usize];
    }
    if let Some(&known) = memo.get(&n) {
        return known;
    }
    memo.insert(n, 0);
    let ways = count(n - 1, memo) + count(n - 2, memo) + count(n - 3, memo);
    ways
}

/// Ways to climb `n` stairs taking 1, 2 or 3 steps at a time.
pub fn climb_ways(n: u64) -> u64 {
    count(n, &mut HashMap::new())
}
