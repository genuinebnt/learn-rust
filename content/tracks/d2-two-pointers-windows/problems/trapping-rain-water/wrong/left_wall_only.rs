pub fn trap(heights: &[u32]) -> u64 {
    let mut left_max = 0u32;
    let mut water = 0u64;
    for &h in heights {
        left_max = left_max.max(h);
        water += (left_max - h) as u64;
    }
    water
}
