pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
    let mut out = Vec::new();
    let (mut lo, mut hi) = new;
    let mut i = 0;
    while i < intervals.len() && intervals[i].1 < lo {
        out.push(intervals[i]);
        i += 1;
    }
    while i < intervals.len() && intervals[i].0 <= hi {
        lo = lo.min(intervals[i].0);
        hi = intervals[i].1;
        i += 1;
    }
    out.push((lo, hi));
    out.extend_from_slice(&intervals[i..]);
    out
}
