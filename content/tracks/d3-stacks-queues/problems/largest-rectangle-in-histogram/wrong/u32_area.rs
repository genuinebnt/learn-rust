pub fn largest_rectangle(heights: &[u32]) -> u64 {
    let mut best = 0u64;
    let mut rising: Vec<usize> = Vec::new();
    for i in 0..=heights.len() {
        let h = heights.get(i).copied().unwrap_or(0);
        while let Some(&top) = rising.last() {
            if heights[top] < h {
                break;
            }
            rising.pop();
            let left = rising.last().map_or(0, |&l| l + 1);
            best = best.max(u64::from(heights[top] * (i - left) as u32));
        }
        rising.push(i);
    }
    best
}
