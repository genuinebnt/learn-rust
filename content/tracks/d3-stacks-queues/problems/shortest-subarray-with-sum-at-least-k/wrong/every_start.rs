pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
    let mut best: Option<usize> = None;
    for i in 0..nums.len() {
        let mut sum = 0;
        for j in i..nums.len() {
            sum += nums[j];
            if sum >= k {
                best = Some(best.map_or(j - i + 1, |b| b.min(j - i + 1)));
                break;
            }
        }
    }
    best
}
