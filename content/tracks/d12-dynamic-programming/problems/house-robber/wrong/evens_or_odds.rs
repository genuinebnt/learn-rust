pub fn rob(nums: &[u32]) -> u64 {
    let even: u64 = nums.iter().step_by(2).map(|&x| x as u64).sum();
    let odd: u64 = nums.iter().skip(1).step_by(2).map(|&x| x as u64).sum();
    even.max(odd)
}
