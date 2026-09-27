fn count(nums: &[u32], target: i64) -> u64 {
    match nums {
        [] => (target == 0) as u64,
        [x, rest @ ..] => count(rest, target - *x as i64) + count(rest, target + *x as i64),
    }
}

pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
    count(nums, target as i64)
}
