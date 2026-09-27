pub fn kth_largest(nums: &mut [i32], k: usize) -> i32 {
    let idx = nums.len() - k;
    *nums.select_nth_unstable(idx).1
}
