pub fn jump(nums: &[u32]) -> Option<usize> {
    let (mut jumps, mut end, mut far) = (0, 0, 0);
    for (i, &step) in nums.iter().enumerate() {
        far = far.max(i + step as usize);
        if i == end {
            if far <= i {
                return None;
            }
            jumps += 1;
            end = far;
        }
    }
    Some(jumps)
}
