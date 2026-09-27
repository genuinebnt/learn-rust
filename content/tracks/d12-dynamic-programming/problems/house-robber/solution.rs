pub fn rob(nums: &[u32]) -> u64 {
    // best_before: best up to house i - 2; best: best up to house i - 1.
    let (mut best_before, mut best) = (0u64, 0u64);
    for &x in nums {
        (best_before, best) = (best, best.max(best_before + x as u64));
    }
    best
}
