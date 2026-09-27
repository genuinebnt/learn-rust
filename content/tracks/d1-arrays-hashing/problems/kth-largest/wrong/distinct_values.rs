pub fn kth_largest(nums: &mut [i32], k: usize) -> i32 {
    let mut v = nums.to_vec();
    v.sort_unstable_by(|a, b| b.cmp(a));
    v.dedup();
    v[(k - 1).min(v.len() - 1)]
}
