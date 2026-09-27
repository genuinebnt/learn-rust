pub fn length_of_lis(nums: &[i32]) -> usize {
    let mut ends_at = vec![1usize; nums.len()];
    for i in 0..nums.len() {
        for j in 0..i {
            if nums[j] < nums[i] {
                ends_at[i] = ends_at[i].max(ends_at[j] + 1);
            }
        }
    }
    ends_at.into_iter().max().unwrap_or(0)
}
