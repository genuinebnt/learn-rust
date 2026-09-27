pub fn min_cost_connect_points(points: &[(i32, i32)]) -> u64 {
    let n = points.len();
    let dist = |a: usize, b: usize| u64::from(points[a].0.abs_diff(points[b].0) + points[a].1.abs_diff(points[b].1));
    // best[v]: the cheapest link from v to the tree so far.
    let mut best = vec![u64::MAX; n];
    let mut inside = vec![false; n];
    let mut total = 0;
    let mut u = 0;
    for _ in 1..n {
        inside[u] = true;
        let mut next = None;
        for v in 0..n {
            if inside[v] {
                continue;
            }
            best[v] = best[v].min(dist(u, v));
            if next.map_or(true, |w: usize| best[v] < best[w]) {
                next = Some(v);
            }
        }
        let v = next.expect("an outside point remains");
        total += best[v];
        u = v;
    }
    total
}
