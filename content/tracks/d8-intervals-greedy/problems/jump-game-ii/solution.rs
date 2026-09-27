pub fn jump(nums: &[u32]) -> Option<usize> {
    let last = nums.len() - 1;
    // Indices up to `end` take `jumps` jumps; `far` is how far one more jump gets.
    let (mut jumps, mut end, mut far) = (0, 0, 0);
    for (i, &step) in nums[..last].iter().enumerate() {
        far = far.max(i + step as usize);
        if i == end {
            if far <= i {
                return None;
            }
            jumps += 1;
            end = far;
            if end >= last {
                break;
            }
        }
    }
    Some(jumps)
}
