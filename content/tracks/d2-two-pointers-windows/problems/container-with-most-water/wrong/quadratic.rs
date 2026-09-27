pub fn max_area(heights: &[u32]) -> u64 {
    let mut best = 0u64;
    for i in 0..heights.len() {
        for j in i + 1..heights.len() {
            best = best.max(heights[i].min(heights[j]) as u64 * (j - i) as u64);
        }
    }
    best
}
