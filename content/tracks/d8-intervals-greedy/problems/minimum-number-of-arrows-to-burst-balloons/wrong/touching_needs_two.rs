pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
    let mut sorted = points.to_vec();
    sorted.sort_unstable_by_key(|p| p.1);
    let mut arrows = 0;
    let mut last: Option<i32> = None;
    for (start, end) in sorted {
        if last.map_or(true, |x| start >= x) {
            arrows += 1;
            last = Some(end);
        }
    }
    arrows
}
