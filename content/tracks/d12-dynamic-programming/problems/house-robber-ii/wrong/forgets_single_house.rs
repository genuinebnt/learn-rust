fn rob_line(nums: &[u32]) -> u64 {
    let (mut best_before, mut best) = (0u64, 0u64);
    for &x in nums {
        (best_before, best) = (best, best.max(best_before + x as u64));
    }
    best
}

pub fn rob(nums: &[u32]) -> u64 {
    if nums.is_empty() {
        return 0;
    }
    rob_line(&nums[1..]).max(rob_line(&nums[..nums.len() - 1]))
}
