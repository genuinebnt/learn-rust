pub fn kth_largest(nums: &mut [i32], k: usize) -> i32 {
    *nums.select_nth_unstable(k - 1).1
}
