pub fn can_jump(nums: &[u32]) -> bool {
    // Every index up to `reach` can be landed on.
    let mut reach = 0usize;
    for (i, &jump) in nums.iter().enumerate() {
        if i > reach {
            return false;
        }
        reach = reach.max(i + jump as usize);
    }
    true
}
