/// The largest sum of `nums[..k]` over k ≥ 1.
pub fn max_prefix_sum(nums: &[i32]) -> Option<i64> {
    let mut sum: i32 = 0;
    let mut best: Option<i64> = None;
    for &x in nums {
        sum = sum.wrapping_add(x);
        best = Some(best.map_or(sum as i64, |b| b.max(sum as i64)));
    }
    best
}
