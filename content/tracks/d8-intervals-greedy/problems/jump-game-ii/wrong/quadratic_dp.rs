pub fn jump(nums: &[u32]) -> Option<usize> {
    let n = nums.len();
    let mut best: Vec<Option<usize>> = vec![None; n];
    best[0] = Some(0);
    for i in 0..n {
        let Some(b) = best[i] else { continue };
        for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
            if best[j].map_or(true, |x| b + 1 < x) {
                best[j] = Some(b + 1);
            }
        }
    }
    best[n - 1]
}
