pub fn split_array(nums: &[u32], k: usize) -> u64 {
    // How many parts are needed if no part may exceed `cap`?
    let parts = |cap: u64| {
        let (mut parts, mut sum) = (1, 0u64);
        for &x in nums {
            let x = u64::from(x);
            if sum + x > cap {
                parts += 1;
                sum = 0;
            }
            sum += x;
        }
        parts
    };
    let mut lo = nums.iter().copied().map(u64::from).max().unwrap_or(0);
    let mut hi: u64 = nums.iter().copied().map(u64::from).sum();
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if parts(mid) <= k {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }
    lo
}
