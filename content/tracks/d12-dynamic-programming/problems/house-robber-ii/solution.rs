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
        // The first and last house can't both be robbed: drop one or the other.
        _ => rob_line(&nums[1..]).max(rob_line(&nums[..nums.len() - 1])),
    }
}
