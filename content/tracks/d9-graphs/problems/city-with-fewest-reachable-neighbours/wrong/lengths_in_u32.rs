pub fn find_the_city(n: usize, roads: &[(usize, usize, u32)], threshold: u32) -> usize {
    const FAR: u32 = u32::MAX / 2;
    let mut dist = vec![vec![FAR; n]; n];
    for (i, row) in dist.iter_mut().enumerate() {
        row[i] = 0;
    }
    for &(a, b, len) in roads {
        dist[a][b] = dist[a][b].min(len);
        dist[b][a] = dist[b][a].min(len);
    }
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                if dist[i][k] + dist[k][j] < dist[i][j] {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }
    let reach = |i: usize| (0..n).filter(|&j| j != i && dist[i][j] <= threshold).count();
    (0..n).rev().min_by_key(|&i| reach(i)).unwrap()
}
