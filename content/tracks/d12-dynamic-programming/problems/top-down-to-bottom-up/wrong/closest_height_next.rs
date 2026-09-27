/// The cheapest way from stone 0 to the last stone, jumping 1 to k stones forward each time.
pub fn min_cost(heights: &[i32], k: usize) -> u64 {
    let n = heights.len();
    let mut total = 0;
    let mut i = 0;
    while i + 1 < n {
        let j = (i + 1..n.min(i + k + 1)).min_by_key(|&j| (heights[i].abs_diff(heights[j]), n - j)).unwrap();
        total += heights[i].abs_diff(heights[j]) as u64;
        i = j;
    }
    total
}
