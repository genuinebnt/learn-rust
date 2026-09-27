/// The cheapest way from stone 0 to the last stone, jumping 1 to k stones forward each time.
pub fn min_cost(heights: &[i32], k: usize) -> u64 {
    fn cost(i: usize, heights: &[i32], k: usize, memo: &mut Vec<Option<u64>>) -> u64 {
        if i + 1 == heights.len() {
            return 0;
        }
        if let Some(c) = memo[i] {
            return c;
        }
        let best = (i + 1..heights.len().min(i + k + 1))
            .map(|j| heights[i].abs_diff(heights[j]) as u64 + cost(j, heights, k, memo))
            .min()
            .unwrap();
        memo[i] = Some(best);
        best
    }

    if heights.is_empty() {
        return 0;
    }
    cost(0, heights, k, &mut vec![None; heights.len()])
}
