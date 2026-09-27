pub fn shortest_subarray(nums: &[i64], k: i64) -> Option<usize> {
    let (mut sum, mut left, mut best) = (0i64, 0usize, None::<usize>);
    for right in 0..nums.len() {
        sum += nums[right];
        while sum >= k && left <= right {
            best = Some(best.map_or(right - left + 1, |b| b.min(right - left + 1)));
            sum -= nums[left];
            left += 1;
        }
    }
    best
}
