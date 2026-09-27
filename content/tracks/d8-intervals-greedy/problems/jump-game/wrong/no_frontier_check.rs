pub fn can_jump(nums: &[u32]) -> bool {
    let far = nums.iter().enumerate().map(|(i, &j)| i + j as usize).max().unwrap_or(0);
    far >= nums.len() - 1
}
