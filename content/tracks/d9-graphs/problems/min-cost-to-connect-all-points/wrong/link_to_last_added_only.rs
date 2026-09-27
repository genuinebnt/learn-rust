pub fn min_cost_connect_points(points: &[(i32, i32)]) -> u64 {
    let n = points.len();
    let dist = |a: usize, b: usize| u64::from(points[a].0.abs_diff(points[b].0) + points[a].1.abs_diff(points[b].1));
    let mut inside = vec![false; n];
    let mut total = 0;
    let mut u = 0;
    for _ in 1..n {
        inside[u] = true;
        let v = (0..n).filter(|&v| !inside[v]).min_by_key(|&v| dist(u, v)).unwrap();
        total += dist(u, v);
        u = v;
    }
    total
}
