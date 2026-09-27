pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable();
    let n = sorted.len();
    // best[i]: most intervals kept among 0..=i when interval i is kept.
    let mut best = vec![1usize; n];
    for i in 0..n {
        for j in 0..i {
            if sorted[j].1 <= sorted[i].0 {
                best[i] = best[i].max(best[j] + 1);
            }
        }
    }
    n - best.into_iter().max().unwrap_or(0)
}
