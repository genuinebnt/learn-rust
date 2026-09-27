pub fn split_array(nums: &[u32], k: usize) -> u64 {
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
    let mut cap = nums.iter().copied().map(u64::from).max().unwrap_or(0);
    while parts(cap) > k {
        cap += 1;
    }
    cap
}
