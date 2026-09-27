pub fn find_maximum_xor(nums: &[u32]) -> u32 {
    let Some(&max) = nums.iter().max() else {
        return 0;
    };
    nums.iter().map(|&x| x ^ max).max().unwrap_or(0)
}
