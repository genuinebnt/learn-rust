pub fn max_product(nums: &[i32]) -> Option<i64> {
    let (&first, rest) = nums.split_first()?;
    let first = first as i64;
    // hi / lo: the largest / smallest product of a subarray ending at the current element.
    let (mut hi, mut lo, mut best) = (first, first, first);
    for &x in rest {
        let x = x as i64;
        let options = [x, hi * x, lo * x];
        hi = *options.iter().max().unwrap();
        lo = *options.iter().min().unwrap();
        best = best.max(hi);
    }
    Some(best)
}
