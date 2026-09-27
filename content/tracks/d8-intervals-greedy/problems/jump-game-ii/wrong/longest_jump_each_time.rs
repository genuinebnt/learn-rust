pub fn jump(nums: &[u32]) -> Option<usize> {
    let last = nums.len() - 1;
    let (mut i, mut jumps) = (0usize, 0usize);
    while i < last {
        if nums[i] == 0 {
            return None;
        }
        i += nums[i] as usize;
        jumps += 1;
    }
    Some(jumps)
}
