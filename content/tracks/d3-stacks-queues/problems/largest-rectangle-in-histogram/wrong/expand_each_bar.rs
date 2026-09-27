pub fn largest_rectangle(heights: &[u32]) -> u64 {
    let mut best = 0u64;
    for i in 0..heights.len() {
        let (mut l, mut r) = (i, i);
        while l > 0 && heights[l - 1] >= heights[i] {
            l -= 1;
        }
        while r + 1 < heights.len() && heights[r + 1] >= heights[i] {
            r += 1;
        }
        best = best.max(u64::from(heights[i]) * (r - l + 1) as u64);
    }
    best
}
