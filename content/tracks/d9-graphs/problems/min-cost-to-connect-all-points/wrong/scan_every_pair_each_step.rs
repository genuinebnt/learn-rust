pub fn min_cost_connect_points(points: &[(i32, i32)]) -> u64 {
    let n = points.len();
    let dist = |a: usize, b: usize| u64::from(points[a].0.abs_diff(points[b].0) + points[a].1.abs_diff(points[b].1));
    let mut inside = vec![false; n];
    inside[0] = true;
    let mut total = 0;
    for _ in 1..n {
        let mut best: Option<(u64, usize)> = None;
        for u in (0..n).filter(|&u| inside[u]) {
            for v in (0..n).filter(|&v| !inside[v]) {
                let d = dist(u, v);
                if best.map_or(true, |(b, _)| d < b) {
                    best = Some((d, v));
                }
            }
        }
        let (d, v) = best.unwrap();
        inside[v] = true;
        total += d;
    }
    total
}
