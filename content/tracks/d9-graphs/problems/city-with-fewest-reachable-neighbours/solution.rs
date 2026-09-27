pub fn find_the_city(n: usize, roads: &[(usize, usize, u32)], threshold: u32) -> usize {
    // u64 so two u32 lengths can be added without overflow.
    let mut dist = vec![vec![u64::MAX; n]; n];
    for (i, row) in dist.iter_mut().enumerate() {
        row[i] = 0;
    }
    for &(a, b, len) in roads {
        let len = u64::from(len);
        dist[a][b] = dist[a][b].min(len);
        dist[b][a] = dist[b][a].min(len);
    }
    // The middle city goes outermost: after round k, paths may pass through cities 0..=k.
    for k in 0..n {
        for i in 0..n {
            if dist[i][k] == u64::MAX {
                continue;
            }
            for j in 0..n {
                if dist[k][j] != u64::MAX && dist[i][k] + dist[k][j] < dist[i][j] {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }
    let reach = |i: usize| (0..n).filter(|&j| j != i && dist[i][j] <= u64::from(threshold)).count();
    // min_by_key keeps the first minimum, so scan from the largest city down.
    (0..n).rev().min_by_key(|&i| reach(i)).expect("n ≥ 2")
}
