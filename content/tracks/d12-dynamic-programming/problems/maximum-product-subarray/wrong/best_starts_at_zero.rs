pub fn max_product(nums: &[i32]) -> Option<i64> {
    if nums.is_empty() {
        return None;
    }
    let (mut hi, mut lo, mut best) = (1i64, 1i64, 0i64);
    for &x in nums {
        let x = x as i64;
        let options = [x, hi * x, lo * x];
        hi = *options.iter().max().unwrap();
        lo = *options.iter().min().unwrap();
        best = best.max(hi);
    }
    Some(best)
}
