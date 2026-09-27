pub fn trap(heights: &[u32]) -> u64 {
    let (mut l, mut r) = (0, heights.len());
    let (mut left_max, mut right_max) = (0u32, 0u32);
    let mut water = 0u32;
    while l < r {
        if heights[l] < heights[r - 1] {
            left_max = left_max.max(heights[l]);
            water += left_max - heights[l];
            l += 1;
        } else {
            right_max = right_max.max(heights[r - 1]);
            water += right_max - heights[r - 1];
            r -= 1;
        }
    }
    water as u64
}
