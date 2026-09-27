pub fn max_area(heights: &[u32]) -> u64 {
    let (mut l, mut r) = (0, heights.len());
    let mut best = 0u64;
    while l + 1 < r {
        let (a, b) = (heights[l], heights[r - 1]);
        best = best.max(a.min(b) as u64 * (r - 1 - l) as u64);
        if a > b {
            l += 1;
        } else {
            r -= 1;
        }
    }
    best
}
