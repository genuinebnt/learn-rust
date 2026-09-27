pub fn split_array(nums: &[u32], k: usize) -> u64 {
    let parts = |cap: u32| {
        let (mut parts, mut sum) = (1, 0u32);
        for &x in nums {
            if sum + x > cap {
                parts += 1;
                sum = 0;
            }
            sum += x;
        }
        parts
    };
    let mut lo = nums.iter().copied().max().unwrap_or(0);
    let mut hi: u32 = nums.iter().sum();
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if parts(mid) <= k {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    u64::from(lo)
}
