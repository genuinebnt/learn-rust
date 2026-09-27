pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable_by_key(|iv| iv.1);
    let mut kept = 0;
    let mut last_end: Option<i32> = None;
    for (start, end) in sorted {
        if last_end.map_or(true, |e| start > e) {
            kept += 1;
            last_end = Some(end);
        }
    }
    intervals.len() - kept
}
