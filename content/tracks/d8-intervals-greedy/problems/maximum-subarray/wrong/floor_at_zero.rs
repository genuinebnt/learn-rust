pub fn max_subarray(nums: &[i32]) -> Option<i64> {
    if nums.is_empty() {
        return None;
    }
    let (mut best, mut current) = (0i64, 0i64);
    for &x in nums {
        current = (current + x as i64).max(0);
        best = best.max(current);
    }
    Some(best)
}
