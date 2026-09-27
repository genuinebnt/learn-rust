pub fn delete_and_earn(nums: &[u32]) -> u64 {
    let mut sorted = nums.to_vec();
    sorted.sort_unstable();
    let (mut before, mut best) = (0u64, 0u64);
    for &x in &sorted {
        (before, best) = (best, best.max(before + x as u64));
    }
    best
}
