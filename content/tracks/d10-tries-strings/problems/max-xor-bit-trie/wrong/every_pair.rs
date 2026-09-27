pub fn find_maximum_xor(nums: &[u32]) -> u32 {
    let mut best = 0;
    for i in 0..nums.len() {
        for j in i + 1..nums.len() {
            best = best.max(nums[i] ^ nums[j]);
        }
    }
    best
}
