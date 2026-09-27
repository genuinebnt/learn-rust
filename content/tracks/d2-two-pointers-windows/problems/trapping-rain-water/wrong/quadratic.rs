pub fn trap(heights: &[u32]) -> u64 {
    (0..heights.len())
        .map(|i| {
            let left = *heights[..=i].iter().max().unwrap();
            let right = *heights[i..].iter().max().unwrap();
            (left.min(right) - heights[i]) as u64
        })
        .sum()
}
