/// The largest sum of `nums[..k]` over k ≥ 1.
pub fn max_prefix_sum(nums: &[i32]) -> Option<i64> {
    let mut sum: i64 = 0;
    let mut best: Option<i64> = None;
    for &x in nums {
        sum += i64::from(x);
        best = Some(best.map_or(sum, |b| b.max(sum)));
    }
    best
}
