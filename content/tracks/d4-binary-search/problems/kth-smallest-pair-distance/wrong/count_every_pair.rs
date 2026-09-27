pub fn smallest_distance_pair(nums: &[i32], k: usize) -> u32 {
    let count = |d: u32| (0..nums.len()).map(|i| (i + 1..nums.len()).filter(|&j| nums[i].abs_diff(nums[j]) <= d).count()).sum::<usize>();
    let (mut lo, mut hi) = (0, u32::MAX);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if count(mid) >= k {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    lo
}
