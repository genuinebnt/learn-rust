pub fn max_subarray(nums: &[i32]) -> Option<i64> {
    let (&first, rest) = nums.split_first()?;
    let (mut best, mut current) = (first, first);
    for &x in rest {
        current = current.wrapping_add(x).max(x);
        best = best.max(current);
    }
    Some(best as i64)
}
