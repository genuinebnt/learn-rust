pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
    nums.windows(k).map(|w| *w.iter().max().unwrap()).collect()
}
