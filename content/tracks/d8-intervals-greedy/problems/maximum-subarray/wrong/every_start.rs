pub fn max_subarray(nums: &[i32]) -> Option<i64> {
    let mut best: Option<i64> = None;
    for i in 0..nums.len() {
        let mut s = 0i64;
        for &x in &nums[i..] {
            s += x as i64;
            best = Some(best.map_or(s, |b| b.max(s)));
        }
    }
    best
}
