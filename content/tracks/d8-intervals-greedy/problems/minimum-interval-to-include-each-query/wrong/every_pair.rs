pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
    queries
        .iter()
        .map(|&q| intervals.iter().filter(|&&(l, r)| l <= q && q <= r).map(|&(l, r)| (r as i64 - l as i64 + 1) as u64).min())
        .collect()
}
