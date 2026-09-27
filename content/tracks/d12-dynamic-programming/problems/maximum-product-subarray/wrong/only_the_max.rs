pub fn max_product(nums: &[i32]) -> Option<i64> {
    let (&first, rest) = nums.split_first()?;
    let (mut hi, mut best) = (first as i64, first as i64);
    for &x in rest {
        let x = x as i64;
        hi = x.max(hi * x);
        best = best.max(hi);
    }
    Some(best)
}
