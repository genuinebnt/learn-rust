fn best(stones: &[u32], diff: i64) -> u32 {
    match stones {
        [] => diff.unsigned_abs() as u32,
        [x, rest @ ..] => best(rest, diff + *x as i64).min(best(rest, diff - *x as i64)),
    }
}

pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
    best(stones, 0)
}
