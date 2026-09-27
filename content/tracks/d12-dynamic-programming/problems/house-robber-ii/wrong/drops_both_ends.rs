fn rob_line(nums: &[u32]) -> u64 {
    let (mut best_before, mut best) = (0u64, 0u64);
    for &x in nums {
        (best_before, best) = (best, best.max(best_before + x as u64));
    }
    best
}

pub fn rob(nums: &[u32]) -> u64 {
    match nums {
        [] => 0,
        [only] => *only as u64,
        [_, mid @ .., _] => rob_line(mid).max(nums[0] as u64),
    }
}
