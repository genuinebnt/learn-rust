pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
    let mut left = points.to_vec();
    left.sort_unstable_by_key(|p| p.1);
    let mut arrows = 0;
    while let Some(&(_, x)) = left.first() {
        arrows += 1;
        left.retain(|&(s, _)| s > x);
    }
    arrows
}
