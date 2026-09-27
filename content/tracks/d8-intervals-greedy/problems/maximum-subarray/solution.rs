pub fn max_subarray(nums: &[i32]) -> Option<i64> {
    let (&first, rest) = nums.split_first()?;
    let mut best = first as i64;
    let mut current = first as i64;
    for &x in rest {
        let x = x as i64;
        current = (current + x).max(x);
        best = best.max(current);
    }
    Some(best)
}
