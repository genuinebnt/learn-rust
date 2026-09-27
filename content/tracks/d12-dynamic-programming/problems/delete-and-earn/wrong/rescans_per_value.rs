pub fn delete_and_earn(nums: &[u32]) -> u64 {
    let max = nums.iter().copied().max().unwrap_or(0);
    let (mut before, mut best) = (0u64, 0u64);
    for v in 0..=max {
        let p = nums.iter().filter(|&&x| x == v).count() as u64 * v as u64;
        (before, best) = (best, best.max(before + p));
    }
    best
}
