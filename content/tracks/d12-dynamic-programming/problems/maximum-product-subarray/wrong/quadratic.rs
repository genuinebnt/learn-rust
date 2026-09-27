pub fn max_product(nums: &[i32]) -> Option<i64> {
    let mut best: Option<i64> = None;
    for i in 0..nums.len() {
        let mut p = 1i64;
        for &x in &nums[i..] {
            p *= x as i64;
            best = Some(best.map_or(p, |b| b.max(p)));
        }
    }
    best
}
