pub fn smallest_distance_pair(nums: &[i32], k: usize) -> u32 {
    let mut v = nums.to_vec();
    v.sort_unstable();
    // Pairs with distance <= d, counted with a sliding window over the sorted values.
    let count = |d: u32| {
        let (mut total, mut left) = (0usize, 0);
        for right in 0..v.len() {
            while v[right].abs_diff(v[left]) > d {
                left += 1;
            }
            total += right - left;
        }
        total
    };
    let (mut lo, mut hi) = (0, v[v.len() - 1].abs_diff(v[0]));
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
