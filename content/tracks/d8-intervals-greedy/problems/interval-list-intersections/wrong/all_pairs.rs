pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
    let mut out = Vec::new();
    for &(s1, e1) in a {
        for &(s2, e2) in b {
            if s1.max(s2) <= e1.min(e2) {
                out.push((s1.max(s2), e1.min(e2)));
            }
        }
    }
    out.sort_unstable();
    out
}
