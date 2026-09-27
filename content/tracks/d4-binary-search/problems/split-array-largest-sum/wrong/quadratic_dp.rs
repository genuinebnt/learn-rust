pub fn split_array(nums: &[u32], k: usize) -> u64 {
    let n = nums.len();
    let mut prefix = vec![0u64; n + 1];
    for i in 0..n {
        prefix[i + 1] = prefix[i] + u64::from(nums[i]);
    }
    let mut best = vec![u64::MAX; n + 1];
    best[0] = 0;
    for _ in 0..k {
        let mut next = vec![u64::MAX; n + 1];
        for i in 1..=n {
            for j in 0..i {
                if best[j] != u64::MAX {
                    next[i] = next[i].min(best[j].max(prefix[i] - prefix[j]));
                }
            }
        }
        best = next;
    }
    best[n]
}
