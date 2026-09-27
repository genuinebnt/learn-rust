pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable();
    let mut out: Vec<(i32, i32)> = Vec::with_capacity(sorted.len());
    for (start, end) in sorted {
        match out.last_mut() {
            Some(last) if start <= last.1 => last.1 = last.1.max(end),
            _ => out.push((start, end)),
        }
    }
    out
}
