pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable();
    let mut out: Vec<(i32, i32)> = Vec::new();
    for (start, end) in sorted {
        match out.iter_mut().find(|m| start <= m.1 && m.0 <= end) {
            Some(m) => m.1 = m.1.max(end),
            None => out.push((start, end)),
        }
    }
    out
}
